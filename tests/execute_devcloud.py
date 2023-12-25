import re
import time
import requests
import json
import copy
import sys
import hashlib
import hmac
import binascii
from datetime import datetime
from optparse import OptionParser

# request_body_temp = "{\"parameter\": [{\"name\": \"SHARE_PATH\",\"value\": \"/home/jenkins/share-data\"},{\"name\": \"CODE_PLATFORM\",\"value\": \"gitee\"},{\"name\": \"ORGANIZATION_NAME\",\"value\": \"mindspore\"},{\"name\": \"REPOSITORY_NAME\",\"value\": \"mindspore\"},{\"name\": \"PIPELINE_TYPE\",\"value\": \"gate\"},{\"name\": \"PIPELINE_BUILD_ID\",\"value\": \"75\"},{\"name\": \"PIPELINE_TASK_TYPE\",\"value\": \"MS_ALL\"},]}"
AK = "9CG2CGRBRF2VTYWIXXK4"
SK = "BpaHSA6BKU3xIlAVIDlnz0rucRW2XZB7O0QpQYbd"
STATUS_CONFIG = ["SUCCESS", "FAILURE", "SCHEDULE_FAILURE", "ABORTED", "UNKNOWN"]
TOKEN = ""
BasicDateFormat = "%Y%m%dT%H%M%SZ"
Algorithm = "SDK-HMAC-SHA256"
HeaderXDate = "X-Sdk-Date"
HeaderHost = "host"
HeaderAuthorization = "Authorization"
HeaderContentSha256 = "x-sdk-content-sha256"


if sys.version_info.major < 3:
    from urllib import quote, unquote


    def hmacsha256(keyByte, message):
        return hmac.new(keyByte, message, digestmod=hashlib.sha256).digest()


    # Create a "String to Sign".
    def StringToSign(canonicalRequest, t):
        bytes = HexEncodeSHA256Hash(canonicalRequest)
        return "%s\n%s\n%s" % (Algorithm, datetime.strftime(t, BasicDateFormat), bytes)

else:
    from urllib.parse import quote, unquote


    def hmacsha256(keyByte, message):
        return hmac.new(keyByte.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()


    # Create a "String to Sign".
    def StringToSign(canonicalRequest, t):
        bytes = HexEncodeSHA256Hash(canonicalRequest.encode('utf-8'))
        return "%s\n%s\n%s" % (Algorithm, datetime.strftime(t, BasicDateFormat), bytes)


def urlencode(s):
    return quote(s, safe='~')


def findHeader(r, header):
    for k in r.headers:
        if k.lower() == header.lower():
            return r.headers[k]
    return None


# HexEncodeSHA256Hash returns hexcode of sha256
def HexEncodeSHA256Hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


def CanonicalRequest(r, signedHeaders):
    canonicalHeaders = CanonicalHeaders(r, signedHeaders)
    hexencode = findHeader(r, HeaderContentSha256)
    if hexencode is None:
        hexencode = HexEncodeSHA256Hash(r.body)
    return "%s\n%s\n%s\n%s\n%s\n%s" % (r.method.upper(), CanonicalURI(r), CanonicalQueryString(r),
                                       canonicalHeaders, ";".join(signedHeaders), hexencode)


def CanonicalURI(r):
    pattens = unquote(r.uri).split('/')
    uri = []
    for v in pattens:
        uri.append(urlencode(v))
    urlpath = "/".join(uri)
    if urlpath[-1] != '/':
        urlpath = urlpath + "/"  # always end with /
    # r.uri = urlpath
    return urlpath


def CanonicalQueryString(r):
    keys = []
    for key in r.query:
        keys.append(key)
    keys.sort()
    a = []
    for key in keys:
        k = urlencode(key)
        value = r.query[key]
        if type(value) is list:
            value.sort()
            for v in value:
                kv = k + "=" + urlencode(str(v))
                a.append(kv)
        else:
            kv = k + "=" + urlencode(str(value))
            a.append(kv)
    return '&'.join(a)


def CanonicalHeaders(r, signedHeaders):
    a = []
    __headers = {}
    for key in r.headers:
        keyEncoded = key.lower()
        value = r.headers[key]
        valueEncoded = value.strip()
        __headers[keyEncoded] = valueEncoded
        if sys.version_info.major == 3:
            r.headers[key] = valueEncoded.encode("utf-8").decode('iso-8859-1')
    for key in signedHeaders:
        a.append(key + ":" + __headers[key])
    return '\n'.join(a) + "\n"


def SignedHeaders(r):
    a = []
    for key in r.headers:
        a.append(key.lower())
    a.sort()
    return a


# Create the HWS Signature.
def SignStringToSign(stringToSign, signingKey):
    hm = hmacsha256(signingKey, stringToSign)
    return binascii.hexlify(hm).decode()


# Get the finalized value for the "Authorization" header.  The signature
# parameter is the output from SignStringToSign
def AuthHeaderValue(signature, AppKey, signedHeaders):
    return "%s Access=%s, SignedHeaders=%s, Signature=%s" % (
        Algorithm, AppKey, ";".join(signedHeaders), signature)



class HttpRequest:
    def __init__(self, method="", url="", headers=None, body=""):
        self.method = method
        spl = url.split("://", 1)
        scheme = 'http'
        if len(spl) > 1:
            scheme = spl[0]
            url = spl[1]
        query = {}
        spl = url.split('?', 1)
        url = spl[0]
        if len(spl) > 1:
            for kv in spl[1].split("&"):
                spl = kv.split("=", 1)
                key = spl[0]
                value = ""
                if len(spl) > 1:
                    value = spl[1]
                if key != '':
                    key = unquote(key)
                    value = unquote(value)
                    if key in query:
                        query[key].append(value)
                    else:
                        query[key] = [value]
        spl = url.split('/', 1)
        host = spl[0]
        if len(spl) > 1:
            url = '/' + spl[1]
        else:
            url = '/'

        self.scheme = scheme
        self.host = host
        self.uri = url
        self.query = query
        if headers is None:
            self.headers = {}
        else:
            self.headers = copy.deepcopy(headers)
        if sys.version_info.major < 3:
            self.body = body
        else:
            self.body = body.encode("utf-8")


class Signer:
    def __init__(self):
        self.Key = ""
        self.Secret = ""

    def Verify(self, r, authorization):
        if sys.version_info.major == 3 and isinstance(r.body, str):
            r.body = r.body.encode('utf-8')
        headerTime = findHeader(r, HeaderXDate)
        if headerTime is None:
            return False
        else:
            t = datetime.strptime(headerTime, BasicDateFormat)

        signedHeaders = SignedHeaders(r)
        canonicalRequest = CanonicalRequest(r, signedHeaders)
        stringToSign = StringToSign(canonicalRequest, t)
        return authorization == SignStringToSign(stringToSign, self.Secret)

    # SignRequest set Authorization header
    def Sign(self, r):
        if sys.version_info.major == 3 and isinstance(r.body, str):
            r.body = r.body.encode('utf-8')
        headerTime = findHeader(r, HeaderXDate)
        if headerTime is None:
            t = datetime.utcnow()
            r.headers[HeaderXDate] = datetime.strftime(t, BasicDateFormat)
        else:
            t = datetime.strptime(headerTime, BasicDateFormat)

        haveHost = False
        for key in r.headers:
            if key.lower() == 'host':
                haveHost = True
                break
        if not haveHost:
            r.headers["host"] = r.host
        signedHeaders = SignedHeaders(r)
        canonicalRequest = CanonicalRequest(r, signedHeaders)
        stringToSign = StringToSign(canonicalRequest, t)
        signature = SignStringToSign(stringToSign, self.Secret)
        authValue = AuthHeaderValue(signature, self.Key, signedHeaders)
        r.headers[HeaderAuthorization] = authValue
        r.headers["content-length"] = str(len(r.body))
        queryString = CanonicalQueryString(r)
        if queryString != "":
            r.uri = r.uri + "?" + queryString


def get_record_info(job_id, build_num):
    """
    获取record_info
    :param job_id:
    :param build_num:
    :return:
    """
    sig = Signer()
    sig.Key = AK
    sig.Secret = SK
    if build_num is None:
        raise "buildNo, please check"
    web = "https://cloudbuild-ext.cn-north-4.myhuaweicloud.com/v3/jobs/{0}/{1}/record-info"
    r = HttpRequest("GET", web.format(job_id, build_num), headers={"x-auth-token": TOKEN})
    sig.Sign(r)
    record_info = requests.request(r.method, url=web.format(job_id, build_num), headers=r.headers,
                                   proxies=no_proxy)
    info_dict = json.loads(record_info.text)
    if "result" in info_dict and isinstance(info_dict["result"], dict):
        result_dict = info_dict["result"]
        if "buildRecordId" in result_dict:
            return result_dict["buildRecordId"]
    return


def get_build_num(job_id):
    """
    获取构建号（build_number）
    :param job_id:
    :return:
    """
    print("job_id: ", job_id)
    web = "https://cloudbuild-ext.cn-north-4.myhuaweicloud.cn/v3/jobs/build"
    sig = Signer()
    sig.Key = AK
    sig.Secret = SK
    body = {"job_id": job_id}
    if request_body != "":
        request_body_dict = eval(request_body)
        body.update(request_body_dict)
    headers = {"Content-Type": "application/json"}
    print(body)
    if TOKEN != "":
        headers["x-auth-token"] = TOKEN
    r = HttpRequest("POST", web, headers=headers, body=json.dumps(body))
    sig.Sign(r)
    job_result = requests.request(r.method, url=web, headers=r.headers, data=r.body,
                                  proxies=no_proxy)
    result_dict = json.loads(job_result.text)
    print(result_dict)
    if "actual_build_number" in result_dict:
        return int(result_dict["actual_build_number"])
    else:
        return


def get_son_record_infos(parent_record_id, times, build_num):
    """
    由父id获取子id
    :param parent_record_id: eg:f7a1bcfe549e4b5eb3047f04b58d5f05
    :param times: eg:34
    :param build_num:
    :return:
    """
    web = "https://cloudbuild-ext.cn-north-4.myhuaweicloud.cn/v3/{0}/flow-graph"
    sig = Signer()
    sig.Key = AK
    sig.Secret = SK
    headers = {}
    if TOKEN != "":
        headers["x-auth-token"] = TOKEN
    r = HttpRequest("GET", web.format(parent_record_id), headers=headers)
    sig.Sign(r)
    n = 0
    son_id_list = []
    while n < times:
        time.sleep(20)
        job_result = requests.request(r.method, url=web.format(parent_record_id), headers=r.headers,
                                      proxies=no_proxy)
        result_dict = json.loads(job_result.text)
        n += 1
        if "result" in result_dict and isinstance(result_dict["result"], dict):
            son_id_dict = {}
            results = result_dict["result"]
            if "vertices" in results and isinstance(results["vertices"], list):
                member_list = results["vertices"]
                for member in member_list:
                    if "id" in member and "status" in member:
                        son_id_dict[member["id"]] = member["status"]
                son_id_list = list(son_id_dict.keys())
                if len(son_id_dict) > 0:
                    need_continue = False
                    for son_job_status in son_id_dict.values():
                        if son_job_status not in STATUS_CONFIG:
                            need_continue = True
                            break
                    if need_continue:
                        print(result_dict)
                        continue
                    else:
                        break
    if n >= times:
        stop_job(jobid, build_num)
        time.sleep(20)
    return son_id_list


def stop_job(job_id, build_num):
    """
    停止任务
    :param job_id:
    :param build_num:
    :return:
    """
    web = "https://cloudbuild-ext.cn-north-4.myhuaweicloud.cn/v3/jobs/stop"
    body = {
        "job_id": job_id,
        "build_no": build_num
    }
    headers = {"Content-Type": "application/json"}
    if TOKEN != "":
        headers["x-auth-token"] = TOKEN
    sig = Signer()
    sig.Key = AK
    sig.Secret = SK
    r = HttpRequest("POST", web, headers=headers, body=json.dumps(body))
    sig.Sign(r)
    for _ in range(5):
        resp = requests.request(r.method, web, headers=r.headers, data=r.body,
                                proxies=no_proxy)
        resp_dict = json.loads(resp.text)
        if "status" in resp_dict and resp_dict["status"] == "success":
            print("stop job {0} success!".format(job_id))
            return
        time.sleep(5)
    raise "error: stop job {0} failed!".format(job_id)


def get_log_info(record_id, compress="false"):
    """
    获取任务日志信息
    :param record_id:
    :param compress:
    :return:
    """
    headers = {"Content-Disposition": "attachment;fileName=" + record_id + ".log",
               "Content-Type": "application/x-download"}
    if TOKEN != "":
        headers["x-auth-token"] = TOKEN
    sig = Signer()
    sig.Key = AK
    sig.Secret = SK
    web = "https://cloudbuild-ext.cn-north-4.myhuaweicloud.cn/v3/{0}/download-log?compress=" + compress
    r = HttpRequest("GET", web.format(record_id), headers=headers)
    sig.Sign(r)
    resp = requests.request(r.method, web.format(record_id), headers=r.headers, proxies=no_proxy)
    print(resp.status_code, resp.reason)
    return resp.text


def apply_for_token(passwd, domain, name):
    """
    请求token
    :param passwd:
    :param domain:
    :param name:
    :return:
    """
    web_domain = "cn-north-4"
    web = "https://iam.{0}.myhuaweicloud.com/v3/auth/tokens".format(web_domain)
    body = {
        "auth": {
            "identity": {
                "password": {
                    "user": {
                        "password": passwd,
                        "domain": {
                            "name": domain
                        },
                        "name": name
                    }
                },
                "methods": [
                    "password"
                ]
            },
            "scope": {
                "project": {
                    "name": web_domain
                }
            }
        }
    }
    token_obj = requests.post(url=web, data=json.dumps(body), proxies=no_proxy)
    print(token_obj.status_code)
    if getattr(token_obj, "headers") and "x-subject-token" in token_obj.headers:
        return token_obj.headers["x-subject-token"]
    raise "get token failed"


def run_build_process(job_id, duration_time):
    """
    运行构建流程
    :param job_id:
    :param duration_time:
    :return:
    """
    print(job_id)
    print(duration_time)
    if jobid == "":
        raise "no job id, please input it in command"
    build_num = get_build_num(job_id)
    if isinstance(build_num, int):
        parent_record = get_record_info(job_id, str(build_num))
        print(parent_record)
        record_id_list = get_son_record_infos(parent_record, duration_time, build_num)
        if record_id_list:
            print(record_id_list)
        for record_id in record_id_list:
            log_info = get_log_info(record_id)
            print(log_info)


if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option('-p', '--password',
                   dest='password',
                   default='',
                   help='password')
    opt.add_option('-u', '--username',
                   dest='username',
                   default='',
                   help='username')
    opt.add_option('-n', '--domain-name',
                   dest='domain_name',
                   default='',
                   help='domain name')
    opt.add_option('-b', '--body',
                   dest='request_body',
                   default='',
                   help='request body, json type')
    opt.add_option('-d', '--duration',
                   dest='duration',
                   default='60s',
                   help='duration of querying the status, example:\n100s、2m、1h、1d')
    opt.add_option('-j', '--jobid',
                   dest='jobid',
                   default='',
                   help='job id')
    opt.parse_args()
    request_body = opt.values.request_body
    duration = opt.values.duration
    jobid = opt.values.jobid  # 653e121ba26d48ad876c4507125745c4
    password = opt.values.password
    username = opt.values.username
    domain_name = opt.values.domain_name
    system_proxy = {"http": "http://proxy.huawei.com:8080",
                    "https": "http://proxy.huawei.com:8080"}
    no_proxy = {"http": None,
                "https": None}
    if re.fullmatch(r"\d+s", duration):
        spent = int(duration.replace("s", "")) / 20
    elif re.fullmatch(r"\d+m", duration):
        spent = int(duration.replace("m", "")) * 3
    elif re.fullmatch(r"\d+h", duration):
        spent = int(duration.replace("h", "")) * 180
    elif re.fullmatch(r"\d+d", duration):
        spent = int(duration.replace("d", "")) * 180 * 24
    else:
        raise "input error duration"
    print(request_body)
    # request_body = request_body_temp  # debug用
    if domain_name != "" and username != "" and password != "":
        apply_for_token(password, domain_name, username)
    run_build_process(jobid, int(spent))
