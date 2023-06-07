import hashlib
import os.path
import threading
import time
import urllib.request

import config
from app.manager.log import log
from app.manager.email_utils import email


class DownloadThread(threading.Thread):
    def __init__(self, url, meta, func=None):
        threading.Thread.__init__(self)
        self.url = url
        self.meta = meta
        self.func = func

    def run(self):
        max_retries = 3
        for i in range(max_retries):
            try:
                url_sha256 = hashlib.sha256(self.url.encode("utf-8")).hexdigest()
                os.makedirs(os.path.join(config.CACHE_DIR, url_sha256))

                import http.client as httplib
                from urllib.parse import urlparse

                parsed_result = urlparse(self.url)
                host = parsed_result.netloc
                host_url = parsed_result.path
                scheme = parsed_result.scheme
                if scheme == "http":
                    port = 80
                elif scheme == "https":
                    port = 443
                else:
                    port = 80

                conn = httplib.HTTPConnection(host, port)
                conn.request('GET', host_url)
                content = conn.getresponse()

                content_disposition = content.getheader("Content-Disposition")
                if content_disposition:
                    file_name = content_disposition.split('filename=')[1].strip('"')
                    log.info(f'content_disposition file_name {file_name}')
                else:
                    file_name = self.url.split("/")[-1]
                    log.info(f'basename file_name {file_name}')

                with open(os.path.join(config.CACHE_DIR, url_sha256, file_name), 'wb') as f:
                    f.write(content.read())

                self.func(self.meta, url_sha256, file_name)
                break
            except Exception as e:
                log.info(f'{self.url}失败{i + 1}次')
                time.sleep(5)
        else:
            log.error(f'{self.url}下载失败三次')
            # email.send_download_fail_mail(self.url)

    @staticmethod
    def local_func(meta, url_sha256, filename):
        meta.update(url_sha256, url_sha256 + "/" + filename)