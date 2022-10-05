import os
from pathlib import Path
from pprint import pprint
from urllib.parse import urlsplit
from dotenv import load_dotenv
import requests


def get_comics_url_and_title(url):

    response = requests.get(url)
    response.raise_for_status()

    comics_info = response.json()

    return comics_info['img'], comics_info['alt']


def load_comics_image(url, folder):

    response = requests.get(url)
    response.raise_for_status()

    filepath = Path(folder).joinpath(urlsplit(url)[2].split('/')[2])

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def get_wall_upload_server(url, group_id, vk_token, v=5.131):
    method_photos_get_wall_upload_server = 'photos.getWallUploadServer'
    params = {
        'access_token': vk_token,
        'group_id': group_id,
        'v': v,
    }
    response = requests.get(f'{url}{method_photos_get_wall_upload_server}', params=params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_groups(url, vk_token, v=5.131, extended=1):
    method = 'groups.get'
    params = {
        'access_token': vk_token,
        'v': v,
        'extended': extended
    }

    response = requests.get(f'{url}{method}', params=params)
    response.raise_for_status()

    return response.json()


def get_wall(vk_token, owner_id, v=5.131):

    params = {
        'access_token': vk_token,
        'v': v,
        'owner_id': -owner_id,
        'filter': 'owner'
    }

    response = requests.get('https://api.vk.com/method/wall.get', params=params)
    response.raise_for_status()

    return response.json()


def upload_photo_on_wall(path, server_url):

    with open(path, 'rb') as photo:
        files = {
            'Content-Type': 'multipart/form-data',
            'photo': photo
        }

        response = requests.post(server_url, files=files)
        response.raise_for_status()

        upload_response = response.json()

        return upload_response['server'], upload_response['photo'], upload_response['hash']


def save_wall_photo(server_id, photo, photo_hash, vk_token, group_id, v=5.131):

        params = {
            'server': server_id,
            'photo': photo,
            'hash': photo_hash,
            'access_token': vk_token,
            'group_id': group_id,
            'v': v,
        }

        response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
        response.raise_for_status()

        save_photo_response = response.json()

        return save_photo_response['response'][0]['owner_id'], save_photo_response['response'][0]['id']


def post_photo_on_wall(vk_group_id, title, photo_owner_id, photo_id, vk_token, v=5.131):

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

    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()

    return response.json()


def main():

    load_dotenv()
    vk_id = os.environ['VK_ID']
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_user_id = os.environ['VK_USER_ID']
    vk_token = os.environ['VK_TOKEN']

    url = 'https://xkcd.com/info.0.json'

    comics_url, comics_title = get_comics_url_and_title('https://xkcd.com/info.0.json')
    destination_folder = 'Comics'
    Path(destination_folder).mkdir(exist_ok=True)
    comics_image_path = load_comics_image(comics_url, destination_folder)

    url_vk = 'https://api.vk.com/method/'

    # Получили ссылку для загрузки на сервер
    upload_server_url = get_wall_upload_server(url_vk, vk_group_id, vk_token)

    # Загрузили фото на стену
    server_id, photo, photo_hash = upload_photo_on_wall(os.path.abspath(comics_image_path), upload_server_url)

    # Сохранили фото на стене
    saved_owner_id, saved_photo_id = save_wall_photo(server_id, photo, photo_hash, vk_token, vk_group_id)

    # Опубликовали фото
    res2 = post_photo_on_wall(vk_group_id, comics_title, saved_owner_id, saved_photo_id, vk_token)
    #pprint(res2)


if __name__ == '__main__':
    main()
