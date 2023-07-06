import hashlib
import os.path
import shutil
import threading
import config

from app.manager.cache_manager import CacheManager, LockException, lock_set
from app.local.local_meta import local_meta
from flask import send_from_directory, redirect
from app.manager.log import log


def get_sha256(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


class LocalManager(CacheManager):
    def __init__(self):
        super().__init__()

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
        threading.Thread(target=self.start_cache, args=(url,)).start()
        log.info(f"{url} not in local, redirect {self.proxy + url}")
        return redirect(self.proxy + url)

    def start_cache(self, url):
        try:
            file_dir, filepath, url_sha256, filename = self.download(url)
            object_key = f'{url_sha256}/{filename}'
            local_meta.update(url_sha256, object_key)
        except LockException as e:
            log.error(f"{e.message}")
        except Exception as e:
            url_sha256 = get_sha256(url)
            # 移除正在下载标识
            lock_set.remove(url_sha256)
            file_dir = os.path.join(config.CACHE_DIR, url_sha256)
            # 防止异常未清理
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir)
            log.error(f'start caching exception, {e}. url, {url}')




