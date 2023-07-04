import hashlib
import os.path
import threading

import wget

import config

from app.manager.cache_manager import CacheManager
from app.local.local_meta import local_meta
from flask import send_from_directory, redirect
from app.manager.log import log


class LocalManager(CacheManager):
    def __init__(self):
        pass

    def is_in_cache(self, url):
        url_sha256 = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return local_meta.is_in_meta(url_sha256)

    def result_in_cache(self, url):
        url_sha256 = hashlib.sha256(url.encode("utf-8")).hexdigest()
        file_addr = local_meta.get_object_key(url_sha256)
        if os.path.exists(os.path.join(config.CACHE_DIR, file_addr)):
            log.info(f"{url} in local, start sending file...")
            return send_from_directory(config.CACHE_DIR, file_addr)
        else:
            local_meta.delete(url_sha256)
            return self.result_not_in_cache(url)

    def result_not_in_cache(self, url):
        log.info(f"{url} not in local, start downloading...")
        threading.Thread(target=LocalManager.download, args=(url,)).start()
        log.info(f"{url} not in local, redirect official url")
        return redirect(url)

    @staticmethod
    def download(url):
        try:
            url_sha256 = hashlib.sha256(url.encode("utf-8")).hexdigest()
            file_dir = os.path.join(config.CACHE_DIR, url_sha256)
            if not os.path.exists(file_dir):
                os.mkdir(file_dir)
            # 防止并发写同一个文件夹。除非发生散列碰撞，否则一个文件夹下只有一个文件。
            if os.listdir(file_dir):
                raise Exception(f"dir has one file, {url_sha256}")
            filepath = wget.download(url, out=file_dir)
            filename = os.path.basename(filepath)
            object_key = f'{url_sha256}/{filename}'
            local_meta.update(url_sha256, object_key)
        except Exception as e:
            log.error(f"download failed, {e}. url, {url}")




