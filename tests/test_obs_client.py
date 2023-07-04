import unittest
from app.obs_manager.obs_client import OBSClient


class TestOBSClient(unittest.TestCase):
    def setUp(self):
        self.obs_client = OBSClient()

    def test_in_obs(self):
        object_key = "0009b09d1ea48d7437acc1aa39d2eaff141de74a17b2be6c7d583960a980c999/rrgtrees.tar.xz"
        result1 = self.obs_client.is_in_obs(object_key)
        object_key = "0009b09d1ea48d7437acc1aa39d2eaff141de74a17b2be6c7d583960a980c999/rrgtrees1.tar.xz"
        result2 = self.obs_client.is_in_obs(object_key)
        self.assertEqual(result1, True)
        self.assertEqual(result2, False)

    def test_get_metadata_url(self):
        key = "0009b09d1ea48d7437acc1aa39d2eaff141de74a17b2be6c7d583960a980c999/rrgtrees.tar.xz"
        metadata_url = self.obs_client.get_metadata_url(key)
        expected_result = "test"
        self.assertEqual(metadata_url, expected_result)

    def test_set_metadata_url(self):
        key = "0009b09d1ea48d7437acc1aa39d2eaff141de74a17b2be6c7d583960a980c999/rrgtrees.tar.xz"
        metadata_url = "test"
        self.obs_client.set_metadata_url(key, metadata_url)

    def test_upload_stream(self):
        url = "http://downloads.sourceforge.net/acpid2/acpid-2.0.34.tar.xz"
        self.obs_client.upload_stream(url)

    def test_get_bucket_acl(self):
        self.obs_client.get_bucket_acl()

    def test_get_object_acl(self):
        object_key = "0009b09d1ea48d7437acc1aa39d2eaff141de74a17b2be6c7d583960a980c999/rrgtrees.tar.xz"
        self.obs_client.get_object_ack(object_key)

    def test_set_object_acl(self):
        object_key = "0009b09d1ea48d7437acc1aa39d2eaff141de74a17b2be6c7d583960a980c999/rrgtrees.tar.xz"
        self.obs_client.set_object_acl(object_key)

    def test_get_object_metadata(self):
        object_key = "0009b09d1ea48d7437acc1aa39d2eaff141de74a17b2be6c7d583960a980c999/rrgtrees.tar.xz"
        self.obs_client.get_object_metadata(object_key)

    def test_get_all_keys(self):
        print(len(self.obs_client.get_all_object_key()))

    def test_delete_all_keys(self):
        pass


if __name__ == '__main__':
    unittest.main()
