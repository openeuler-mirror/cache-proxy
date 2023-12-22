import hashlib
import os
import threading
import wget
import config

from app.manager.log import log


class SetLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.sets = set()

    def in_set(self, value):
        with self.lock:
            return value in self.sets

    def remove(self, value):
        with self.lock:
            if value in self.sets:
                self.sets.remove(value)

    def add(self, value):
        with self.lock:
            self.sets.add(value)


lock_set = SetLock()
lock = threading.Lock()


class LockException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class CacheManager:
    def __init__(self):
        self.proxy = config.PROXY_URL

    def download(self, url):
        url_sha256 = hashlib.sha256(url.encode("utf-8")).hexdigest()
        with lock:
            if lock_set.in_set(url_sha256):
                raise LockException(f"{url} is downloading")
            else:
                lock_set.add(url_sha256)
        file_dir = os.path.join(config.CACHE_DIR, url_sha256)
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        filepath = wget.download(self.proxy + url, out=file_dir)
        filename = os.path.basename(filepath)
        log.info(f"download to local success, url: {url}, filename: {filename}")
        # 下载完成
        lock_set.remove(url_sha256)
        if "." in filename:
            suffix = filename.split(".")[-1]
            if suffix not in config.SUFFIX:
                log.error("This kind of package has no permission: " + filename)
                return
        return file_dir, filepath, url_sha256, filename

    def is_in_cache(self, url):
        pass

    def result_in_cache(self, url):
        pass

    def result_not_in_cache(self, url):
        pass


