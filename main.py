import os
import pathlib
import random
import urllib.parse
from pprint import pprint
from urllib.parse import urlparse
from dotenv import load_dotenv
import requests


class VkErrors(Exception):
    ...


def get_comics_url_and_title():

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    max_comics_count = response.json()['num']

    random.seed()
    comics_index = random.randint(0, max_comics_count)

    url = fr'https://xkcd.com/{comics_index}/info.0.json'

    response = requests.get(url)
    response.raise_for_status()
    comics_info = response.json()
    return comics_info['img'], comics_info['alt']


def download_comics_image(url):

    response = requests.get(url)
    response.raise_for_status()

    file_path = urllib.parse.unquote(urlparse(url).path)
    path, file_name = os.path.split(file_path)

    with open(file_name, 'wb') as file:
        file.write(response.content)

    return file_name


def get_wall_upload_server_url(group_id, vk_token, v=5.131):

    url_method = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'access_token': vk_token,
        'group_id': group_id,
        'v': v,
    }

    response = requests.get(
        url_method,
        params=params,
    )

    response_message = response.json()

    try:
        upload_url = response_message['response']['upload_url']

        return upload_url

    except KeyError:
        raise VkErrors(response_message['error']['error_msg'])


def upload_photo_on_wall(path, server_url):

    with open(path, 'rb') as photo:
        files = {
            'Content-Type': 'multipart/form-data',
            'photo': photo
        }

        response = requests.post(
            server_url,
            files=files,
        )

    upload_response = response.json()

    try:
        upload_server = upload_response['server']
        upload_photo = upload_response['photo']
        upload_hash = upload_response['hash']

        return upload_server, upload_photo, upload_hash

    except KeyError:
        raise VkErrors(upload_response['error']['error_msg'])


def save_photo_to_wall(server_id, photo, photo_hash,
                       vk_token, group_id, v=5.131
                       ):

    params = {
        'server': server_id,
        'photo': photo,
        'hash': photo_hash,
        'access_token': vk_token,
        'group_id': group_id,
        'v': v,
    }

    response = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params=params,
    )

    save_photo_response = response.json()

    try:
        owner_id = save_photo_response['response'][0]['owner_id']
        photo_id = save_photo_response['response'][0]['id']

        return owner_id, photo_id

    except KeyError:
        raise VkErrors(save_photo_response['error']['error_msg'])


def post_photo_on_wall(vk_group_id, title, photo_owner_id,
                       photo_id, vk_token, v=5.131
                       ):

    params = {
        'v': v,
        'access_token': vk_token,
        'owner_id': f'-{vk_group_id}',
        'from_group': -1,
        'message': title,
        'attachments': {
            f'photo{photo_owner_id}_{photo_id}'
        }
    }

    response = requests.post(
        'https://api.vk.com/method/wall.post',
        params=params,
    )
    post_photo_response = response.json()

    try:
        return post_photo_response['response']
    except KeyError:
        raise VkErrors(post_photo_response['error']['error_msg'])


def main():

    load_dotenv()
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_token = os.environ['VK_TOKEN']

    try:
        comics_url, comics_title = get_comics_url_and_title()

        comics_image_path = download_comics_image(comics_url)

        upload_server_url = get_wall_upload_server_url(
            vk_group_id,
            vk_token
        )

        server_id, photo, photo_hash = upload_photo_on_wall(
            os.path.abspath(comics_image_path),
            upload_server_url
        )

        pathlib.Path(comics_image_path).unlink(missing_ok=True)

        saved_owner_id, saved_photo_id = save_photo_to_wall(
            server_id, photo,
            photo_hash,
            vk_token,
            vk_group_id
        )

        post_photo_on_wall(
            vk_group_id,
            comics_title,
            saved_owner_id,
            saved_photo_id,
            vk_token
        )

    except requests.exceptions.HTTPError as response_error:
        print('Ошибка запроса', response_error.errno)

    except VkErrors as error:
        print('Ошибка в запросе к VK API:', error)


if __name__ == '__main__':
    main()
