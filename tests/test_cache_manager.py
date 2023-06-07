import unittest
from app.obs_manager.obs_manager import OBSManager


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache_manager = OBSManager()


if __name__ == '__main__':
    unittest.main()
