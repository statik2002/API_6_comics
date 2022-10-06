import os
import pathlib
import random
import time
from urllib.parse import urlsplit
from dotenv import load_dotenv
import requests


def get_comics_url_and_title():

    random.seed()
    comics_index = random.randint(0, 999)

    url = fr'https://xkcd.com/{comics_index}/info.0.json'

    connection_timeout = 60

    while True:
        try:
            response = requests.get(url, timeout=connection_timeout)
            response.raise_for_status()
            comics_info = response.json()
            return comics_info['img'], comics_info['alt']

        except requests.exceptions.HTTPError:
            comics_index = random.randint(0, 999)
            url = fr'https://xkcd.com/{comics_index}/info.0.json'

        except requests.exceptions.ConnectionError:
            connection_timeout += 5
            time.sleep(2)
            continue


def load_comics_image(url):

    connection_timeout = 60

    while True:
        try:
            response = requests.get(url, timeout=connection_timeout)
            response.raise_for_status()

            file_path = urlsplit(url)[2].split('/')[2]

            with open(file_path, 'wb') as file:
                file.write(response.content)

            return file_path

        except requests.exceptions.HTTPError:
            print('Ошибка при скачивании комикса')
            return None

        except requests.exceptions.ConnectionError:
            connection_timeout += 5
            time.sleep(2)
            continue


def get_wall_upload_server_url(url, group_id, vk_token, v=5.131):

    connection_timeout = 60
    method_wall_upload_server = 'photos.getWallUploadServer'
    params = {
        'access_token': vk_token,
        'group_id': group_id,
        'v': v,
    }

    while True:
        try:
            response = requests.get(
                f'{url}{method_wall_upload_server}',
                params=params,
                timeout=connection_timeout
            )
            response.raise_for_status()
            return response.json()['response']['upload_url']

        except requests.exceptions.HTTPError:
            print('Ошибка запроса получения адреса сервера')
            return None

        except requests.exceptions.ConnectionError:
            connection_timeout += 5
            time.sleep(5)
            continue


def upload_photo_on_wall(path, server_url):

    connection_timeout = 60

    try:
        with open(path, 'rb') as photo:
            files = {
                'Content-Type': 'multipart/form-data',
                'photo': photo
            }

            while True:
                try:
                    response = requests.post(
                        server_url,
                        files=files,
                        timeout=connection_timeout
                    )
                    response.raise_for_status()

                    upload_response = response.json()

                    return (
                        upload_response['server'],
                        upload_response['photo'],
                        upload_response['hash']
                    )

                except requests.exceptions.HTTPError:
                    print('Ошибка при загрузке изображения')
                    return None

                except requests.exceptions.ConnectionError:
                    connection_timeout += 5
                    time.sleep(5)
                    continue

    except FileNotFoundError:
        print(f'Файл {path} не найден!')
        return


def save_photo_to_wall(server_id, photo, photo_hash, vk_token, group_id, v=5.131):
    connection_timeout = 60

    params = {
        'server': server_id,
        'photo': photo,
        'hash': photo_hash,
        'access_token': vk_token,
        'group_id': group_id,
        'v': v,
    }

    while True:
        try:
            response = requests.post(
                'https://api.vk.com/method/photos.saveWallPhoto',
                params=params,
                timeout=connection_timeout
            )
            response.raise_for_status()

            save_photo_response = response.json()

            return (
                save_photo_response['response'][0]['owner_id'],
                save_photo_response['response'][0]['id']
            )

        except requests.exceptions.HTTPError:
            print('Ошибка при сохранении изображения')
            return None

        except requests.exceptions.ConnectionError:
            connection_timeout += 5
            time.sleep(5)
            continue


def post_photo_on_wall(vk_group_id, title, photo_owner_id,
                       photo_id, vk_token, v=5.131
                       ):

    connection_timeout = 60
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

    while True:
        try:
            response = requests.post(
                'https://api.vk.com/method/wall.post',
                params=params,
                timeout=connection_timeout
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError:
            print('Ошибка при публикации комикса')
            return None

        except requests.exceptions.ConnectionError:
            connection_timeout += 5
            time.sleep(5)
            continue


def main():

    load_dotenv()
    vk_group_id = os.environ['VK_GROUP_ID']
    vk_token = os.environ['VK_TOKEN']
    vk_url = 'https://api.vk.com/method/'

    comics_url, comics_title = get_comics_url_and_title()

    comics_image_path = load_comics_image(comics_url)
    if not comics_image_path:
        return

    upload_server_url = get_wall_upload_server_url(
        vk_url,
        vk_group_id,
        vk_token
    )
    if not upload_server_url:
        return

    server_id, photo, photo_hash = upload_photo_on_wall(
        os.path.abspath(comics_image_path),
        upload_server_url
    )
    if not server_id:
        return

    saved_owner_id, saved_photo_id = save_photo_to_wall(
        server_id, photo,
        photo_hash,
        vk_token,
        vk_group_id
    )
    if not saved_owner_id:
        return

    post_photo_on_wall(
        vk_group_id,
        comics_title,
        saved_owner_id,
        saved_photo_id,
        vk_token
    )

    pathlib.Path(comics_image_path).unlink(missing_ok=True)


if __name__ == '__main__':
    main()
