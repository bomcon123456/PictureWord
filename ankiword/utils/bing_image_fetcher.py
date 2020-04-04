# Much of logic and code is from ostrolucky/Bulk-Bing-Image-downloader.
# All I did is OOP and change a little bit so that it works on my situation.
# Greatly thanks to you <3!

import os
from pathlib import Path
import urllib.request
import re
import threading
import posixpath
import urllib.parse
import time
import hashlib
import pickle
import imghdr
import multiprocessing


class BingImageFetcher:

    # config
    async_bing_url = 'https://www.bing.com/images/async?q='

    urlopenheader = {
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0)' +
        'Gecko/20100101 Firefox/60.0'
    }

    def __init__(self, output_dir='../data/imgs', timeout=5):
        self.output_dir = output_dir
        self.timeout = timeout

    def get_filename_from_url(self, url, save_name):
        path = urllib.parse.urlsplit(url).path
        filename = posixpath.basename(path)\
            .split('?')[0]  # Strip GET parameters from filename
        name, ext = os.path.splitext(filename)
        name = name[:36].strip()
        if not ext:
            ext = '.jpg'

        return save_name + ext

    def _download_img_read_md5(self, url, filename):
        # Get image data buffer
        request = urllib.request.Request(url, None, self.urlopenheader)
        image = urllib.request.urlopen(request).read()
        # Check if the buffer is an image
        if not imghdr.what(None, image):
            print('Invalid image, not saving ' + filename)
            return

        md5_key = hashlib.md5(image).hexdigest()
        return image, md5_key

    def _download(self, pool_sema: threading.Semaphore,
                  url: str, save_name: str):

        pool_sema.acquire()
        filename = self.get_filename_from_url(url, save_name)
        try:
            image, md5_key = self._download_img_read_md5(url, filename)

            i = 0
            # If we see a file in folder has this name:
            # First we check whether it is the same image
            # If not, add an index to the filename so that we can differentiate.
            # Else, we stop saving.
            full_path_to_file = os.path.join(self.output_dir, filename)
            while os.path.exists(full_path_to_file):
                opened_image = open(full_path_to_file, 'rb')
                if hashlib.md5(opened_image.read()).hexdigest() == md5_key:
                    print('Already downloaded ' + filename + ', not saving')
                    return
                i += 1
                filename = "%s-%d%s" % (name, i, ext)

            imagefile = open(full_path_to_file, 'wb')
            imagefile.write(image)
            imagefile.close()
            print("File downloaded: " + filename)
        except Exception:
            print("Fail to download: " + filename)
        finally:
            pool_sema.release()

    def _get_bing_url(self, keyword, current, adlt, filters):
        # Return the url as this example:
        # https://www.bing.com/images/async?q="apple"&first=10&count=35&adlt=1&qft=''
        if not filters:
            filters = ''
        request_url = self.async_bing_url + \
            urllib.parse.quote_plus(keyword) + '&first=' + \
            str(current) + '&count=35&adlt=' + adlt + \
            '&qft=' + filters

        request = urllib.request.Request(
            request_url, None, headers=self.urlopenheader)
        response = urllib.request.urlopen(request)

        # Scrape from HTML links to images
        html = response.read().decode('utf8')
        # regex: murl":"(.*?)"
        links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)

        return links

    def _fetch_images_from_keyword(self, pool_sema: threading.Semaphore,
                                   keyword: str, adlt: str, limit: int,
                                   filters=None, out_dir=None):
        current = 0
        last = ''
        while True:
            links = self._get_bing_url(keyword, current, adlt, filters)
            threads_arr = []
            try:
                # In the next loop, if the last link we find is the previous last
                # We stop the loop
                if links[-1] == last:
                    return
                # Go for each links we find by the regex, download
                for index, link in enumerate(links):
                    if limit is not None and current + index >= limit:
                        return threads_arr
                    t = multiprocessing.Process(target=self._download, args=(
                        pool_sema, link, keyword+str(index)))
                    threads_arr.append(t)
                    current += 1
                last = links[-1]

            except IndexError:
                print('No search results for "{0}"'.format(keyword))
                return

    def download_from_word(self, word, limit=30, threads=5,
                           adult=True, filters=None):

        word = word.strip().lower()

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        pool_sema = threading.BoundedSemaphore(threads)

        print('Starting fetching')
        adult = '' if adult else 'off'
        th = self._fetch_images_from_keyword(
            pool_sema, word, adult, limit)

        for t in th:
            t.start()

        for t in th:
            t.join(timeout=self.timeout)

            if t.is_alive():
                t.terminate()


if __name__ == "__main__":
    fetcher = BingImageFetcher()
    fetcher.download_from_word('kind', limit=50)
    # fetcher.download_from_word('apple', limit=50)
    # fetcher.download_from_word('tree', limit=50)
