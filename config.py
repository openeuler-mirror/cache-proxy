# config.py
OPEN_OBS = True

# OBS configuration
OBS_ACCESS_KEY_ID = ""
OBS_SECRET_ACCESS_KEY = ""
OBS_ENDPOINT = ""
OBS_BUCKET_NAME = ""

# Cache directory
CACHE_DIR = r"/tmp/.cache"

# Open Proxy Rules
OPEN_PROXY_RULES = True
SUFFIX = ['sign', 'tgz', 'tbz', 'mim', '0', 'pom', 'xpi', 'lzma', 'tex', 'ls', 'wget', 'xsd', 'root', 'java', 'gpg',
          'gz', 'bz2', 'el', 'md', 'rb', 'pdf', 'sha256sum', 'ml', "bz2'", 'xz', 'jar', 'txz', 'gem', 'ttf', 'oxt',
          'json', 'tbz2', 'sh', 'awk', 'pem', 'zip', 'asc', 'dat', 'py', 'properties', 'distribution-zip', 'js', 'c',
          'rpm', '7z', 'txt', 'html', 'sig', 'dtd', 'pod', 'whl', 'xml']
URL_WHITE_LIST = []

# proxy
PROXY_URL = ""