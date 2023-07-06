import sys
import os

import config
from flask import Flask, abort
from app.manager.cache_manager_factory import CacheManagerFactory
from app.manager.proxy_manager import ProxyManager
from app.manager.log import log

sys.path.append(os.path.abspath(os.getcwd()))

# 检查CACHE_DIR是否存在，如果不存在则创建
if not os.path.exists(config.CACHE_DIR):
    try:
        os.makedirs(config.CACHE_DIR)
    except OSError:
        sys.exit(f"创建目录 {config.CACHE_DIR} 失败。请检查你的权限。")

# 检查我们是否有写入CACHE_DIR的权限
if not os.access(config.CACHE_DIR, os.W_OK):
    sys.exit(f"无法写入 {config.CACHE_DIR} 。请检查你的权限。")

# 检查我们是否有从CACHE_DIR读取的权限
if not os.access(config.CACHE_DIR, os.R_OK):
    sys.exit(f"无法从 {config.CACHE_DIR} 读取。请检查你的权限。")

app = Flask(__name__)

open_obs = config.OPEN_OBS
cache_manager = CacheManagerFactory.get_manager(open_obs)

proxy_manager = ProxyManager()
access = proxy_manager.always_access if proxy_manager.close_or_none() else proxy_manager.rules_filter


@app.route('/')
def home():
    return 'Welcome to openEuler upstream cache proxy!'


@app.route('/download/')
def empty_info():
    return "empty url, please add url to the end!"


@app.route('/download/<path:url>')
def download(url):
    # 检查url
    if not url.startswith("https://") and not url.startswith("http://"):
        log.warning(f"bad url:{url} try access")
        abort(400, 'Bad download url')
    # 未通过规则，拒绝服务
    if not access(url):
        log.warning(f"bad file type: {url} try access")
        abort(400, 'Prohibited by proxy rule')
    # 查询缓存信息
    if cache_manager.is_in_cache(url):
        return cache_manager.result_in_cache(url)
    else:
        return cache_manager.result_not_in_cache(url)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)
