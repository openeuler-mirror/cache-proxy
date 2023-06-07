import unittest
from app.obs_manager.obs_client import OBSClient


class TestOBSClient(unittest.TestCase):
    def setUp(self):
        self.obs_client = OBSClient()

    def test_in_obs(self):
        object_key = "sample-kernel-python3.zip"
        self.obs_client.is_in_obs(object_key)

    def test_get_metadata_url(self):
        print(self.obs_client.get_metadata_url("boost_%{version_enc}.tar.gz"))
        print(self.obs_client.get_metadata_url("busybox-%{VERSION}.tar.bz2"))
        print(self.obs_client.get_metadata_url("crypto-policies-git%{git_commit_hash}.tar.gz"))
        print(self.obs_client.get_metadata_url("test/adcli-0.9.2.tar.gz"))

    def test_get_url_key_dict(self):
        print(self.obs_client.get_url_key_dict())

    def test_set_metadata_url(self):
        self.obs_client.set_metadata_url("sample-kernel-python3.zip", "https://1/sample-kernel-python3.zip")

    def test_upload_stream(self):
        host = "downloads.sourceforge.net"
        host_url = "/acpid2/acpid-2.0.34.tar.xz"
        # port = 443
        port = 80
        url = "http://downloads.sourceforge.net/acpid2/acpid-2.0.34.tar.xz"
        self.obs_client.upload_stream(host, port, host_url, url)

    def test_get_bucket_acl(self):
        self.obs_client.get_bucket_acl()

    def test_get_object_acl(self):
        object_key = "netkit-ftp-0.17.tar.gz"
        self.obs_client.get_object_ack(object_key)

    def test_set_object_acl(self):
        object_key = "netkit-ftp-0.17.tar.gz"
        self.obs_client.set_object_acl(object_key)

    def test_get_object_metadata(self):
        self.obs_client.get_object_metadata("bridge-utils-1.7.1.tar.gz")
        self.obs_client.get_object_metadata("v%{_version}.tar.gz")
        print(self.obs_client.get_metadata_url("v%{_version}.tar.gz"))

    def test_get_all_keys(self):
        print(self.obs_client.get_all_object_key())

    def test_delete_all_keys(self):
        self.obs_client.delete_all()


if __name__ == '__main__':
    unittest.main()
