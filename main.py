import os
from pathlib import Path
from pprint import pprint
from urllib.parse import urlsplit
from dotenv import load_dotenv
import requests


def get_comics_url(url):

    response = requests.get(url)
    response.raise_for_status()

    return response.json()['img']


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
    return response.json()


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


def save_wall_photo(path, server, vk_token, group_id, v=5.131):

    with open(path, 'rb') as photo:
        files = {
            'Content-Type': 'multipart/form-data',
            'photo': photo
        }

        response = requests.post(server, files=files)
        response.raise_for_status()

        res2=response.json()
        pprint(res2)

        params = {
            'server': res2['server'],
            'photo': res2['photo'],
            'hash': res2['hash'],
            'access_token': vk_token,
            'group_id': group_id,
            'v': v,
        }

        response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
        response.raise_for_status()

        pprint(response.json())

    return response.json()


def main():

    load_dotenv()
    vk_id = os.environ['VK_ID']
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_user_id = os.environ['VK_USER_ID']
    vk_token = os.environ['VK_TOKEN']

    url = 'https://xkcd.com/info.0.json'

    comics_url = get_comics_url('https://xkcd.com/info.0.json')
    destination_folder = 'Comics'
    Path(destination_folder).mkdir(exist_ok=True)

    comics_image_path = load_comics_image(comics_url, destination_folder)
    #print(comics_image_path)

    url_vk = 'https://api.vk.com/method/'

    #get_all_groups = get_groups(url_vk, vk_token)
    #pprint(get_all_groups)

    upload_server = get_wall_upload_server(url_vk, vk_group_id, vk_token)
    #pprint(upload_server)


    #print(os.path.abspath(comics_image_path))

    upload_photo_response = save_wall_photo(
        os.path.abspath(comics_image_path),
        upload_server['response']['upload_url'],
        vk_token,
        vk_group_id
    )
    #print(upload_photo_response)


if __name__ == '__main__':
    main()
