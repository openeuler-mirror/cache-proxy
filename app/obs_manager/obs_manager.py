import hashlib
import os
import shutil
import threading

import config
from app.obs_manager.obs_client import obs_client
from app.manager.cache_manager import CacheManager
from app.obs_manager.obs_meta import obs_meta
from app.manager.log import log
from flask import redirect


def get_sha256(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


class OBSManager(CacheManager):
    def __init__(self):
        pass

    def is_in_cache(self, url):
        url_sha256 = get_sha256(url)
        return obs_meta.is_in_meta(url_sha256)

    def result_in_cache(self, url):
        url_sha256 = get_sha256(url)
        object_key = obs_meta.get_object_key(url_sha256)
        obs_url = obs_client.get_obs_download_url(object_key)
        log.info(f"{url} in obs, redirect obs url")
        return redirect(obs_url)

    def result_not_in_cache(self, url):
        log.info(f"{url} not in obs, start uploading file to obs")
        threading.Thread(target=OBSManager.do_upload, args=(url,)).start()
        log.info(f"{url} not in obs, redirect official url")
        return redirect(url)

    @staticmethod
    def do_upload(url):
        try:
            object_key = obs_client.upload_file(url)
            url_sha256 = get_sha256(url)
            obs_meta.update(url_sha256, object_key)
        except IOError as e:
            log.error(f'{e}')
        except Exception as e:
            url_sha256 = get_sha256(url)
            file_dir = os.path.join(config.CACHE_DIR, url_sha256)
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir)
            log.error(f'upload exception, {e}. url, {url}')




