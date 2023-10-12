import hashlib
import os
import shutil
import threading
from urllib.parse import quote
import config

from app.obs_manager.obs_client import obs_client
from app.manager.cache_manager import CacheManager, LockException, lock_set
from app.obs_manager.obs_meta import obs_meta
from app.manager.log import log
from flask import redirect


def get_sha256(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


class OBSManager(CacheManager):
    def __init__(self):
        super().__init__()

    def is_in_cache(self, url):
        url_sha256 = get_sha256(url)
        return obs_meta.is_in_meta(url_sha256)

    def result_in_cache(self, url):
        url_sha256 = get_sha256(url)
        object_key = obs_meta.get_object_key(url_sha256)
        obs_url = obs_client.get_obs_download_url(object_key)
        basename = os.path.basename(obs_url)
        obs_url = obs_url.replace(basename, quote(basename))
        log.info(f"{url} in obs, redirect obs url")
        return redirect(obs_url)

    def result_not_in_cache(self, url):
        log.info(f"{url} not in obs, start caching")
        threading.Thread(target=self.start_cache, args=(url, )).start()
        log.info(f"{url} not in obs, redirect {self.proxy + url}")
        return redirect(self.proxy + url)

    def start_cache(self, url):
        try:
            file_dir, filepath, url_sha256, filename = self.download(url)
            object_key = obs_client.upload_file(file_dir, filepath, url_sha256, filename)
            obs_meta.update(url_sha256, object_key)
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir)
        except LockException as e:
            log.error(f"{e}")
        except Exception as e:
            url_sha256 = get_sha256(url)
            # 移除正在下载标识
            lock_set.remove(url_sha256)
            file_dir = os.path.join(config.CACHE_DIR, url_sha256)
            # 防止异常未清理
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir)
            log.error(f'start caching exception, {e}. url, {url}')




