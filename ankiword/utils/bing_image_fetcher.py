# Much of logic and code is from ostrolucky/Bulk-Bing-Image-downloader.
# All I did is OOP and change a little bit so that it works on my situation.
# Greatly thanks to you <3!

import os
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

    def __init__(self, output_dir='./bing', timeout=5):
        self.tried_urls = []
        self.image_md5s = {}
        self.in_progress = 0
        self.output_dir = output_dir
        self.timeout = timeout

    def _download(self, pool_sema: threading.Semaphore, url: str):
        if url in self.tried_urls:
            return

        pool_sema.acquire()
        self.in_progress += 1

        path = urllib.parse.urlsplit(url).path
        filename = posixpath.basename(path)\
            .split('?')[0]  # Strip GET parameters from filename
        name, ext = os.path.splitext(filename)
        name = name[:36].strip()

        filename = name + ext

        try:
            # Get image data buffer
            request = urllib.request.Request(url, None, self.urlopenheader)
            image = urllib.request.urlopen(request).read()
            # Check if the buffer is an image
            if not imghdr.what(None, image):
                print('Invalid image, not saving ' + filename)
                return

            # Check duplicate images
            md5_key = hashlib.md5(image).hexdigest()
            if md5_key in self.image_md5s:
                print('Image is a duplicate of ' +
                      self.image_md5s[md5_key] + ', not saving ' + filename)
                return

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

            self.image_md5s[md5_key] = filename

            imagefile = open(full_path_to_file, 'wb')
            imagefile.write(image)
            imagefile.close()
            print("OK: " + filename)
            self.tried_urls.append(url)
        except Exception:
            print("FAIL: " + filename)
        finally:
            pool_sema.release()
            self.in_progress -= 1

    def _fetch_images_from_keyword(self, pool_sema: threading.Semaphore,
                                   keyword: str, adlt: str, limit: int,
                                   filters=None, out_dir=None):
        current = 0
        last = ''

        while True:
            time.sleep(0.1)

            if self.in_progress > 10:
                continue
            if not filters:
                filters = ''

            # Return the url as this example:
            # https://www.bing.com/images/async?q="apple"&first=10&count=35&adlt=1&qft=''
            request_url = self.async_bing_url + \
                urllib.parse.quote_plus(keyword) + '&first=' + \
                str(current) + '&count=35&adlt=' + adlt + \
                '&qft=' + filters

            request = urllib.request.Request(
                request_url, None, headers=self.urlopenheader)
            response = urllib.request.urlopen(request)

            # Scrape from HTML links to images
            html = response.read().decode('utf8')
            # murl":"(.*?)"
            links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            threads_arr = []
            try:
                # If we reach the end, finish
                if links[-1] == last:
                    return
                # Go for each links we find by the regex, download
                for index, link in enumerate(links):
                    print(index)
                    if limit is not None and current + index >= limit:
                        return threads_arr
                    t = multiprocessing.Process(target=self._download, args=(
                        pool_sema, link))
                    # self._download(pool_sema, link)
                    threads_arr.append(t)
                    current += 1
                last = links[-1]

            except IndexError:
                print('No search results for "{0}"'.format(keyword))
                return

    def _backup_history(self):
        download_history = open(os.path.join(
            self.output_dir, 'download_history.pickle'), 'wb')
        print('Currently saving accessed link to db...')
        pickle.dump(self.tried_urls, download_history)

        copied_image_md5s = dict(self.image_md5s)
        pickle.dump(copied_image_md5s, download_history)
        download_history.close()
        print('history_dumped')

    def download_from_word(self, word, limit=30, threads=5,
                           adult='', filters=None):

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        pool_sema = threading.BoundedSemaphore(threads)

        print('Starting fetching')
        th = self._fetch_images_from_keyword(
            pool_sema, word, adult, limit)

        for t in th:
            t.start()

        for t in th:
            t.join(timeout=self.timeout)

            if t.is_alive():
                t.terminate()

    # def download_from_file(self, file_src, limit=30, threads=5,
    #                        adult='', filters=None):
    #     try:
    #         inputFile = open(file_src)
    #     except (OSError, IOError):
    #         print("Couldn't open file {}".format(file_src))
    #         raise Exception
    #     pool_sema = threading.BoundedSemaphore(threads)

    #     for keyword in inputFile.readlines():
    #         output_sub_dir = os.path.join(
    #             self.output_dir, keyword.strip().replace(' ', '_'))
    #         if not os.path.exists(output_sub_dir):
    #             os.makedirs(output_sub_dir)
    #         self._fetch_images_from_keyword(
    #             pool_sema, keyword,
    #             adult, limit, out_dir=output_sub_dir)

    #         self._backup_history()
    #         time.sleep(10)
    #     inputFile.close()


if __name__ == "__main__":
    fetcher = BingImageFetcher()
    fetcher.download_from_word('Apple')
