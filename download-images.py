"""
Download and preprocess images for the ImageGraph dataset.

Before running this script, please download the URL lists from
https://github.com/nle-ml/mmkb and unpack. Images will (by defaul) be stored as
`image-graph_images/{freebase-id}/{provider}_{index}.jpg`. All images will be
converted to jpg and rescaled to a maximum size of 500 while preserving the
aspect ratio. Uses multiprocessing to download and process the images in
parallel. Skips images that were already downloaded.


usage: download-images.py [-h] [--url-dir URL_DIR] [--images-dir IMAGES_DIR]
                          [--provider {all,google,bing,yahoo}]
                          [--num-images NUM_IMAGES] [--workers WORKERS]

optional arguments:
  -h, --help            show this help message and exit
  --url-dir URL_DIR     the directory where the url files are stored (default:
                        image-graph_urls)
  --images-dir IMAGES_DIR
                        the directory where the processed images will be
                        stored (default: image-graph_images)
  --provider {all,google,bing,yahoo}
                        download only images from this provider (default: all)
  --num-images NUM_IMAGES
                        the number of images to download per provider
                        (default: 25)
  --workers WORKERS     the number of workers (should be much higher than your
                        number of cores because many workers will get stuck
                        waiting for server responses) (default: 100)
"""


from __future__ import absolute_import, division, print_function, unicode_literals
import pandas as pd
import urllib
from urllib.parse import urlparse
from PIL import Image, ImageFile
from tqdm import tqdm
import os
import errno
from ssl import CertificateError
from http.client import HTTPException
from multiprocess import Pool
import multiprocess as mp
import sys
import argparse
# import socket
from socket import socket
import urllib.request
from multiprocessing import Process



def download_image(i):
    provider = 'bing'
    providers = ['google', 'bing', 'yahoo']
    temp_path = r"C:\Users\Shantam Saxena\OneDrive\Documents\Projects\graph_convolution_networks\image-graph_urls"
    urls = pd.read_csv(os.path.join(temp_path, 'URLS_{}.txt'.format(provider)), sep='\t', names=['url', 'id'])
    row = urls.iloc[i]
    url = row['url']
    freebase_id, index = row['id'].split('/')
    index = int(index)

    # Create dir for entity if it doesn't exist.
    target_dir = os.path.join('image-graph_urls/downloaded_images', freebase_id)
    try:
        os.makedirs(target_dir)
    except OSError as e:  # multiprocessing-safe way to handle existing dir
        if e.errno != errno.EEXIST:
            raise

    # TODO: Maybe use more images if some cannot be downloaded.
    if index < 25:  # only use first 25 images (as in the paper)
        target_filename = '{}_{}.jpg'.format(provider, index)

        # Skip images that were already downloaded.
        if os.path.exists(os.path.join(target_dir, target_filename)):
            pass
        else:
            try:
                # Download and open image.
                # TODO: Store temporary files in a separate folder (e.g. image-graph_temp),
                #       so they are not hidden in the system folders.
                temp_filename = ''
                temp_filename, _ = urllib.request.urlretrieve(row['url'])
                im = Image.open(temp_filename)
            except (IOError, CertificateError, HTTPException):
                pass
            except Exception as e:
                print('Got unusual error during downloading/opening of image:', e)
                print('Please make sure that this error is just caused by a corrupted file.')
            else:
                # Resize and convert to jpg.
                im.thumbnail((500, 500), Image.ANTIALIAS)
                im = im.convert('RGB')

                # Save.
                im.save(os.path.join(target_dir, target_filename))
            finally:
                # Remove temporary file.
                try:
                    os.remove(temp_filename)
                except OSError:
                    pass



if __name__ == '__main__':

    ImageFile.LOAD_TRUNCATED_IMAGES = True  # prevent PIL from raising an error if a file is truncated
    # socket.setdefaulttimeout(30)  # set timeout for downloads so processes do not get completely stuck
    # socket.settimeout(30)
    parser = argparse.ArgumentParser(description='Download images for ImageGraph.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--url-dir', default='image-graph_urls', help='the directory where the url files are stored')
    parser.add_argument('--images-dir', default='image-graph_images', help='the directory where the processed images will be stored')
    parser.add_argument('--provider', choices=['all', 'google', 'bing', 'yahoo'], default='all', help='download only images from this provider')
    parser.add_argument('--num-images', type=int, default=25, help='the number of images to download per provider')
    parser.add_argument('--workers', type=int, default=1, help='the number of workers (should be much higher than your number of cores because many workers will get stuck waiting for server responses)')
    # args = parser.parse_args()

    # if args.provider == 'all':
    #     providers = ['google', 'bing', 'yahoo']
    # else:
    #     providers = [args.provider]

    providers = ['google', 'bing', 'yahoo']
    provider = 'bing'
# for provider in providers:
    # args = parser.parse_args()
    

    print('Downloading images for:', provider)
    temp_path = r"C:\Users\Shantam Saxena\OneDrive\Documents\Projects\graph_convolution_networks\image-graph_urls"


    # pool = Pool(args.workers)  # use many processes here because some of them will get stuck waiting for server responses
    urls = pd.read_csv(os.path.join(temp_path, 'URLS_{}.txt'.format(provider)), sep='\t', names=['url', 'id'])
    print(urls.shape)

    # with mp.Pool(2) as pool:
    #     ii = 
    #     print(ii)
    #     print(pool.map(download_image,ii))
        
    # for i in urls.index.to_list():
    #     download_image(i)
    # with tqdm(total=urls.shape[0]) as pbar:
    #     for _ in pool.imap_unordered(download_image, urls.index, 100):
    #         pbar.update()

    p = mp.Pool(30)
    indices = urls.index
    p.map(download_image, indices)


    print()
    print('Finished:', provider)
    print()