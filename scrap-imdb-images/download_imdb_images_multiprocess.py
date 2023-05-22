"""This script download the 10K images for male and female and store in the 
corresponding directories. Male images are stroed in male directory and female 
images are stored in female directory.
"""

import os
import re
import time

import urllib
import requests
from bs4 import BeautifulSoup

from functools import partial
from multiprocessing import Pool


class DownloadIMDBImages:
    """Download number of images from the IMDB website and save local computer. 
    """
    def __init__(self, base_url, count, gender, storage_path, img_to_download):
        self.base_url = base_url
        self.gender = gender
        self.count = count
        self.img_download_cnt = 0
        self.storage_path = storage_path
        self.img_to_download = img_to_download

    def get_img_download_cnt(self):
        """Get the number of images downloaded.
        """
        return self.img_download_cnt

    def set_img_download_cnt(self, cnt):
        """Set the number of images download count.
        """
        self.img_download_cnt = cnt

    def download_page_images(self, start):
        """Download the images from IMDB for a specific page and returns the total 
        number of images downloaded.
        """
        # set the headers
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

        # form the url with query params
        url = self.base_url.format(self.gender, self.count, start)
        print(f"Downloading from url={url}")
        time.sleep(2)

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Something went while downloading images, error code={response.status_code}")
        
        # parse the HTML response
        result = BeautifulSoup(response.content,'html.parser')
        image_divs = result.find_all('div', class_='lister-item mode-detail')

        # iterate through images listed on the page
        for img_div in image_divs:
            image_url = img_div.find('img')['src']
            image_name = img_div.find('img')['alt']
    
            #file_name = re.sub('[^a-zA-Z\d\s_-]', " ", image_name)
            target_file_path = os.path.join(self.storage_path, image_name + ".jpg")
            
            if os.path.exists(target_file_path):
                print(f"Skipping......file already exists, filename={target_file_path}")
                continue
            
            try:
                # download the image to local computer
                urllib.request.urlretrieve(image_url, target_file_path)
                self.img_download_cnt += 1
            except Exception as err:
                print(f"Encountred error while downloading image, url={image_url}")
            
            # exit if reach to desired image download count
            if self.img_download_cnt >= self.img_to_download:
                break

        return self.img_download_cnt
    
        
if __name__ == "__main__":
    execution_time = 0
    img_per_page = 100  # images listed per page
    img_to_download = 1000 # number of images to download
    base_url = "https://www.imdb.com/search/name/?gender={}&count={}&start={}&ref_=rlm"

    # create a parent directory to store images if not exists
    if not os.path.exists("IMDB"):
            os.mkdir("IMDB")
            
    # download images for gender
    for gender in ['male', 'female']:
        start = time.perf_counter() # start time of the script
        tot_img_downloaded = 0  # total images downloaded
        
        # create path to store images under parent dir
        storage_path = os.path.join("IMDB", gender)
        if not os.path.exists(storage_path):
            os.mkdir(storage_path)
        
        download_obj = DownloadIMDBImages(base_url, img_per_page, gender, storage_path, img_to_download)
        
        print(f"Downloading {gender} images from IMDB")
        # create multiple process to reduce download time
        with Pool() as p :
            download_count = p.map(download_obj.download_page_images, range(1, img_to_download+1, img_per_page))
        
        tot_img_downloaded= sum(download_count)
        download_obj.set_img_download_cnt(tot_img_downloaded)
        print(f"Total images downloaded till: {tot_img_downloaded}")
        
        # download remaining images if any
        page_start = img_to_download + 1
        print(f"Downloading remaining images= {img_to_download-tot_img_downloaded}")
        while tot_img_downloaded < img_to_download:
            res = download_obj.download_page_images(page_start)
            page_start = page_start + img_per_page
            tot_img_downloaded = res
       
        finish = time.perf_counter()    # script end time
        execution_time += (finish-start)
        print(f"Completed downloading images={tot_img_downloaded} for gender={gender}")

    print(f'Download took {execution_time/60: .2f} minute(s) to finish')
