from app.local.local_manager import LocalManager
from app.obs_manager.obs_manager import OBSManager


class CacheManagerFactory:
    @staticmethod
    def get_manager(config):
        if config:
            return OBSManager()
        else:
            return LocalManager()
