import hashlib
import os.path
import shutil
import urllib.request

import wget

import config


from obs import ObsClient
from app.manager.log import log


class OBSClient:
    def __init__(self):
        self.client = ObsClient(access_key_id=config.OBS_ACCESS_KEY_ID,
                                secret_access_key=config.OBS_SECRET_ACCESS_KEY,
                                server=config.OBS_ENDPOINT)

    def is_in_obs(self, object_key):
        try:
            resp = self.client.getObjectMetadata(config.OBS_BUCKET_NAME, object_key)

            if resp.status < 300:
                return True
            else:
                return False
        except Exception as e:
            log.error(f'{e}')

    def get_all_object_key(self):
        try:
            keys = []
            max_num = 1000
            mark = None
            while True:
                resp = self.client.listObjects(config.OBS_BUCKET_NAME, marker=mark, max_keys=max_num)
                if resp.status < 300:
                    for content in resp.body.contents:
                        keys.append(content.key)
                    if resp.body.is_truncated is True:
                        mark = resp.body.next_marker
                    else:
                        break
                else:
                    log.error(f'errorCode:,{resp.errorCode} errorMessage:, {resp.errorMessage}')
            return keys
        except Exception as e:
            log.error(f'{e}')

    def get_metadata_url(self, object_key):
        try:
            resp = self.client.getObjectMetadata(config.OBS_BUCKET_NAME, object_key)

            if resp.status < 300:
                header_dict = dict(resp.header)
                url = header_dict['url'] if 'url' in header_dict else ""
                return url
            else:
                log.warning(f'{object_key} not in obs')
        except Exception as e:
            log.error(f'{e}')

    def set_metadata_url(self, object_key, url):
        try:
            from obs import SetObjectMetadataHeader

            # 设置对象元数据
            metadata = {'url': url}

            resp = self.client.setObjectMetadata(config.OBS_BUCKET_NAME, object_key, metadata=metadata)

            if resp.status < 300:
                log.info(f'set {object_key} url = {url} success')
            else:
                log.error(f'set {object_key} url = {url} fail errorCode:,{resp.errorCode} errorMessage:, {resp.errorMessage}')
        except Exception as e:
            log.error(f'{e}')

    def upload_stream(self, url):
        # 在上层捕获异常
        import http.client as httplib
        from urllib.parse import urlparse

        parsed_result = urlparse(url)
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

        url_sha256 = hashlib.sha256(url.encode("utf-8")).hexdigest()
        content_disposition = content.getheader("Content-Disposition")
        if content_disposition:
            file_name = content_disposition.split('filename=')[1].strip('"')
            log.info(f'content_disposition file_name {file_name}')
        else:
            file_name = url.split("/")[-1]
            log.info(f'basename file_name {file_name}')
        object_key = f'{url_sha256}/{file_name}'

        resp = self.client.putContent(config.OBS_BUCKET_NAME, object_key, content=content)

        if resp.status < 300:
            log.info(f'from {url} upload {object_key} success. requestId:, {resp.requestId}')
            self.set_object_acl(object_key)
        else:
            log.error(f'from {url} upload {object_key} fail, {resp.errorCode} errorMessage:, {resp.errorMessage}')
            raise Exception("from {url} upload {object_key} fail")

        return object_key

    def upload_file(self, url):
        url_sha256 = hashlib.sha256(url.encode("utf-8")).hexdigest()
        file_dir = os.path.join(config.CACHE_DIR, url_sha256)
        if os.path.exists(file_dir):
            raise IOError(f"dir already exits, {file_dir}")
        os.mkdir(file_dir)
        filepath = wget.download(url, out=file_dir)
        filename = os.path.basename(filepath)
        object_key = f'{url_sha256}/{filename}'

        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                resp = self.client.putContent(config.OBS_BUCKET_NAME, url_sha256 + "/" + filename, content=f)
                if resp.status < 300:
                    log.info(f"upload successful, {object_key}")
                    self.set_object_acl(object_key)
                else:
                    raise Exception(f"upload failed, {object_key}")
        else:
            raise Exception(f'download failed,{url}')

        if os.path.exists(file_dir):
            shutil.rmtree(file_dir)

        return object_key


    def get_obs_download_url(self, object_key):
        return f'https://{config.OBS_BUCKET_NAME}.{config.OBS_ENDPOINT}/{object_key}'

    def get_bucket_acl(self):
        try:
            resp = self.client.getBucketAcl(config.OBS_BUCKET_NAME)

            if resp.status < 300:
                print('requestId:', resp.requestId)
                print('owner_id:', resp.body.owner.owner_id)
                print('owner_name:', resp.body.owner.owner_name)
                index = 1
                for grant in resp.body.grants:
                    print('grant [' + str(index) + ']')
                    print('grant_id:', grant.grantee.grantee_id)
                    print('grant_name:', grant.grantee.grantee_name)
                    print('group:', grant.grantee.group)
                    print('permission:', grant.permission)
                    index += 1
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
        except:
            import traceback
            print(traceback.format_exc())

    def get_object_ack(self, object_key):
        try:
            resp = self.client.getObjectAcl(config.OBS_BUCKET_NAME, object_key)

            if resp.status < 300:
                print('requestId:', resp.requestId)
                print('owner_id:', resp.body.owner.owner_id)
                print('owner_name:', resp.body.owner.owner_name)

                index = 1
                for grant in resp.body.grants:
                    print('grant [' + str(index) + ']')
                    print('grantee_id:', grant.grantee.grantee_id)
                    print('grantee_name:', grant.grantee.grantee_name)
                    print('group:', grant.grantee.group)
                    print('permission:', grant.permission)
                    index += 1
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
        except:
            import traceback
            print(traceback.format_exc())

    def set_object_acl(self, object_key):
        from obs import HeadPermission

        # 设置对象为公共读
        resp = self.client.setObjectAcl(config.OBS_BUCKET_NAME, object_key, aclControl=HeadPermission.PUBLIC_READ)
        if resp.status < 300:
            log.info(f"setting {object_key} = PUBLIC_READ succeeded")
        else:
            raise Exception(f"Failed to set {object_key} = PUBLIC_READ")


    def get_object_metadata(self, object_key):
        try:
            resp = self.client.getObjectMetadata(config.OBS_BUCKET_NAME, object_key)

            if resp.status < 300:
                print('requestId:', resp.requestId)
                print('etag:', resp.body.etag)
                print('lastModified:', resp.body.lastModified)
                print('contentType:', resp.body.contentType)
                print('contentLength:', resp.body.contentLength)
            else:
                print('status:', resp.status)
        except:
            import traceback
            print(traceback.format_exc())

    def delete_all(self):
        try:
            from obs import DeleteObjectsRequest, Object

            object_keys = self.get_all_object_key()
            objects = [Object(key=object_key) for object_key in object_keys]

            resp = self.client.deleteObjects(config.OBS_BUCKET_NAME, DeleteObjectsRequest(quiet=False, objects=objects))

            if resp.status < 300:
                print('requestId:', resp.requestId)
                if resp.body.deleted:
                    index = 1
                    for delete in resp.body.deleted:
                        print('delete[' + str(index) + ']')
                        print('key:', delete.key, ',deleteMarker:', delete.deleteMarker, ',deleteMarkerVersionId:',
                              delete.deleteMarkerVersionId)
                        print('versionId:', delete.versionId)
                        index += 1
                if resp.body.error:
                    index = 1
                    for err in resp.body.error:
                        print('err[' + str(index) + ']')
                        print('key:', err.key, ',code:', err.code, ',message:', err.message)
                        print('versionId:', err.versionId)
                        index += 1
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
        except:
            import traceback
            print(traceback.format_exc())


obs_client = OBSClient()
