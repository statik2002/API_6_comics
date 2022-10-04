import os
from pathlib import Path
from pprint import pprint
from urllib.parse import urlsplit
from dotenv import load_dotenv
import requests


def load_comics_image(url, folder):

    response = requests.get(url)
    response.raise_for_status()

    filepath = Path(folder).joinpath(urlsplit(url)[2].split('/')[2])

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def main():

    load_dotenv()
    vk_id = os.environ['VK_ID']
    vk_user_id = os.environ['VK_USER_ID']
    vk_token = os.environ['VK_TOKEN']

    url = 'https://xkcd.com/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    comics_description = response.json()

    destination_folder = 'Comics'
    Path(destination_folder).mkdir(exist_ok=True)

    print(comics_description['alt'])
    load_comics_image(comics_description['img'], destination_folder)

    url_vk = 'https://api.vk.com/method/groups.get'

    params = {
        'access_token': vk_token,
        'v': 5.131,
        'extended': 1
    }

    response = requests.get(url_vk, params=params)
    response.raise_for_status()
    pprint(response.json())


if __name__ == '__main__':
    main()
