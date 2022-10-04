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


def getwalluploadserver(url, vk_group_id, vk_token, v=5.131, extended=1):
    method_photos_getwalluploadserver = 'photos.getWallUploadServer'
    params = {
        'access_token': vk_token,
        'v': v,
        'extended': extended,
        'group_id': vk_group_id,
    }
    response = requests.get(f'{url}{method_photos_getwalluploadserver}', params=params)
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


def upload_image_at_wall(url, vk_token, vk_user_id, vk_group_id, path, upload_server):

    print(f'{url}photos.saveWallPhoto')

    params = {
            'user_id': vk_user_id,
            'group_id': vk_group_id,
            'server': upload_server,
            'access_token': vk_token,
    }

    with open(path, 'rb') as photo:
        files = {
            'multipart/form-data': photo,
        }
        response = requests.post(f'{url}photos.saveWallPhoto', files=files, params=params)
        response.raise_for_status()

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

    upload_server = getwalluploadserver(url_vk, vk_group_id, vk_token)
    pprint(upload_server)

    #print(os.path.abspath(comics_image_path))

    upload_photo_response = upload_image_at_wall(
        url_vk,
        vk_token,
        upload_server['response']['user_id'],
        vk_group_id,
        os.path.abspath(comics_image_path),
        upload_server['response']['upload_url']
    )
    print(upload_photo_response)


if __name__ == '__main__':
    main()
