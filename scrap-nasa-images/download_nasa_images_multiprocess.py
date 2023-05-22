"""Download all images from NASA website and store on local computer using 
Python multiprocessing approach.
"""

import re
import os
import time
import json
import requests
import urllib
import traceback
from multiprocessing import Pool


class DownloadNasaImages:
    def __init__(self):
        self.base_url = "https://earthobservatory.nasa.gov/images/getRecords?page={}"
        self.image_dir = "images"

    def download_page_images(self, page):
        # set request headers
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

        url = self.base_url.format(page)
        print(f"Downloading from url={url}")
        time.sleep(2)
        
        data = {}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Something went while downloading images, error code={response.status_code}")
        
        #get the json response
        res_json = response.json()
        images_details = res_json['data']
        for image in images_details:
            title = image['title']
            desc = image['caption_short']
            
            data[title] = desc
            image_url = image['image_path'] + image['thumbnail_file']
            image_url = image_url.replace(" ", "%20")
            # print(image_url)    

            # replace special characters from the image name
            new_title = re.sub('[^a-zA-Z\d_-]', " ", title)
            target_file_path = os.path.join(self.image_dir, new_title + ".jpg")
            # print(target_file_path)
            
            # if image already exists then skip downloading
            if os.path.exists(target_file_path):
                print(f"Skipping......file already exists, filename={target_file_path}")
                print(url)
                continue
            try:
                # download the image to local computer
                urllib.request.urlretrieve(image_url, target_file_path)
            except Exception as err:
                print(f"Encounterd an exception while downloading image: {err}")
                traceback.print_stack()

        return data


if __name__ == "__main__":
    start = time.perf_counter()

    total_pages = 2958  # total number of pages to download
    images_data = {}    # dict to hold the images data

    # create the parent directory if not exists
    if not os.path.exists("images"):
        os.mkdir("images")

    obj = DownloadNasaImages()

    # create multiple processes to reduce download time
    with Pool() as pool:
        # execute tasks in order
        for result in pool.map(obj.download_page_images, range(1, total_pages+1)):
            # update the image info dict
            images_data.update(result)
    
    # write the image info data to json file
    with open("nasa_output.json", "w") as outjson:
        json.dump(images_data, outjson, indent=4)

    finish = time.perf_counter()

    print(f'Downloading script took {(finish-start)/60: .2f} minute(s) to finish')
