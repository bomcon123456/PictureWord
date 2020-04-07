# Much of logic and code is from ostrolucky/Bulk-Bing-Image-downloader.
# All I did is OOP and change a little bit so that it works on my situation.
# Greatly thanks to you <3!
import imghdr
import hashlib
import urllib.parse
import posixpath
import threading
import re
import urllib.request
from pathlib import Path
import os
from . import __path__ as ROOT_PATH
module_path = ROOT_PATH[0]


class BingImageFetcher:

    # config
    async_bing_url = 'https://www.bing.com/images/async?q='

    urlopenheader = {
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0)' +
        'Gecko/20100101 Firefox/60.0'
    }

    def __init__(self, output_dir='{}/../data/imgs'.format(module_path), timeout=5):
        self.output_dir = output_dir
        self.timeout = timeout

    @staticmethod
    def get_filename_from_url(url, save_name):
        path = urllib.parse.urlsplit(url).path
        filename = posixpath.basename(path)\
            .split('?')[0]  # Strip GET parameters from filename
        name, ext = os.path.splitext(filename)
        name = name[:36].strip()
        if not ext:
            ext = '.jpg'

        return save_name + ext

    @classmethod
    def _download_img_read_md5(cls, url, filename):
        # Get image data buffer
        request = urllib.request.Request(url, None, cls.urlopenheader)
        image = urllib.request.urlopen(request).read()
        # Check if the buffer is an image
        if not imghdr.what(None, image):
            print('Invalid image, not saving ' + filename)
            return

        md5_key = hashlib.md5(image).hexdigest()
        return image, md5_key

    @classmethod
    def _download(cls, pool_sema: threading.Semaphore,
                  url: str, save_name: str, output_dir: str):

        pool_sema.acquire()
        filename = cls.get_filename_from_url(url, save_name)
        try:
            image, md5_key = cls._download_img_read_md5(url, filename)

            i = 0
            # If we see a file in folder has this name:
            # First we check whether it is the same image
            # If not, add index to the filename so that we can differentiate.
            # Else, we stop saving.
            full_path_to_file = os.path.join(output_dir, filename)
            while os.path.exists(full_path_to_file):

                opened_image = open(full_path_to_file, 'rb')
                if hashlib.md5(opened_image.read()).hexdigest() == md5_key:
                    print('Already downloaded ' + filename + ', not saving')
                    return
                name, ext = filename.split('.')
                i += 1
                filename = "%s-%d.%s" % (name, i, ext)

            imagefile = open(full_path_to_file, 'wb')
            imagefile.write(image)
            imagefile.close()
            # print("File downloaded: " + filename)
        except Exception:
            # print("Fail to download: " + filename)
            pass
        finally:
            pool_sema.release()

    @classmethod
    def _get_bing_url(cls, keyword, current, adlt, filters):
        # Return the url as this example:
        # https://www.bing.com/images/async?q="apple"&first=10&count=35&adlt=1&qft=''
        if not filters:
            filters = ''
        request_url = cls.async_bing_url + \
            urllib.parse.quote_plus(keyword) + '&first=' + \
            str(current) + '&count=35&adlt=' + adlt + \
            '&qft=' + filters

        request = urllib.request.Request(
            request_url, None, headers=cls.urlopenheader)
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
                    t_event = threading.Event()
                    t = threading.Thread(target=self._download, args=(
                        pool_sema, link, keyword+str(index), out_dir))
                    current += 1
                    t.start()
                    threads_arr.append((t, t_event))
                last = links[-1]

            except IndexError:
                print('No search results for "{0}"'.format(keyword))
                return

    def download_from_word(self, word, limit=30, threads=5,
                           adult=True, filters=None):

        word = word.strip().lower()
        output_dir = self.output_dir + '/' + word

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pool_sema = threading.BoundedSemaphore(threads)

        print('Downloading...')
        adult = '' if adult else 'off'
        th = self._fetch_images_from_keyword(
            pool_sema, word, adult, limit, out_dir=output_dir)

        for t, t_event in th:
            t.join(self.timeout)

            if t.is_alive():
                # print('Thread not done, setting to kill.')
                t_event.set()
            else:
                # print("Thread finished")
                pass

            t.join()

        p = Path(output_dir)
        return list(map(lambda x: str(x.resolve()), p.glob(word+'*')))


if __name__ == "__main__":
    import socket

    socket.setdefaulttimeout(2)

    fetcher = BingImageFetcher()
    print(fetcher.download_from_word('kind', limit=50))
    # fetcher.download_from_word('apple', limit=50)
    # fetcher.download_from_word('tree', limit=50)
