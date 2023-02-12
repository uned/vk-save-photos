import os
import shutil
import sys
import vk
import requests
import re
from random import randint
from time import sleep

# Define constants

# Required!
# Get it from https://oauth.vk.com/authorize?client_id=6449285&response_type=token&scope=84
access_token = "vk-access-token"

# user id
user_id = 1234567890

# ---------------------------
# optional
# vk api batch size for photos in album
api_batch_size = 1000

# already downloaded albums counter
# use it to continue downloading, not from the beginning
already_downloaded = 0


def create_folder(folder_name):
    '''Create a folder to store photos named after your VK
    first and last name.'''

    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)
    return folder_name


def photos_downloader(url, folder_name):
    '''Download all the photos into folder_name'''

    file_name = url.split('?')[0].split('/')[-1]
    s = requests.Session()
    r = s.get(url, stream=True)

    if r.status_code == 200:
        with open(os.path.join(folder_name, file_name), "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

if __name__ == '__main__':
    try:
        api = vk.API(access_token=access_token)
        print("Authentication: success")

    except Exception:
        print("Authentication : failed")
        sys.exit(1)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected!")
        sys.exit(0)

    try:
        user = api.users.get(user_ids=user_id, v=5.131)[0]
        folder = create_folder(user["first_name"] + '_' + user["last_name"])

        albums = api.photos.getAlbums(owner_id=user_id, need_system=1, v=5.131)["items"]
        max_i = len(albums)
        i = 0

        for a in albums:
            if (a["id"] > 0 and i > already_downloaded):
                photos = api.photos.get(owner_id=user_id, album_id=a["id"], count=api_batch_size, v=5.131)["items"]
                max_j = len(photos)
                j = 1

                for p in photos:
                    photo_resolutions = sorted(p["sizes"], key=lambda a: a['height'], reverse=True)
                    url = photo_resolutions[0]["url"]
                    album_folder = folder + '\\' + str(a["id"]) + '_' + re.sub(r'["<>/\\*?|]', '_', a["title"].strip())
                    create_folder(album_folder)
                    photos_downloader(url, folder_name=album_folder)
                    print("\r Albums {} / {}, Photos {} / {}".format(i, max_i, j, max_j))
                    j = j + 1
                    #sleep(randint(5, 30)/100)

            i = i + 1

    except Exception as e:
        print(e)
        sys.exit(1)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected!")
        sys.exit(0)

