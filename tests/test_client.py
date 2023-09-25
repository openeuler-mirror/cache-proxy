import os
import threading
import time

import requests
from pyrpm.spec import Spec, replace_macros


def test():
    sources_dict = {}
    p_path = r"C:\Users\xxx\Downloads\pkgs_without_tar-master\pkgs_without_tar-master\pkgs"
    pkgs = os.listdir(p_path)
    for pkg in pkgs:
        f_path = os.path.join(p_path, pkg)
        if not os.path.isdir(f_path):
            continue
        files = os.listdir(f_path)
        for f_name in files:
            if f_name.endswith(".spec"):
                spec = Spec.from_file(os.path.join(f_path, f_name))
                for source in spec.sources:
                    s = replace_macros(source, spec)
                    if s.startswith("http:") or s.startswith("https:"):
                        sources_dict[s] = f_name
    # print(len(sources))
    # for i in range(11001):
    #     print(sources[i])

    with open(r"C:\Users\xxx\Downloads\pkgs_without_tar-master\pkgs_without_tar-master\sources_dict1.txt", 'w') as f:
        for source in sources_dict:
            f.write(sources_dict[source] + " " + source + "\n")
    with open(r"C:\Users\xxx\Downloads\pkgs_without_tar-master\pkgs_without_tar-master\sources_dict.txt", 'r') as f:
        sources_dict = {s.strip().split()[1]: s.strip().split()[0] for s in f.readlines()}
    sources = list(sources_dict.keys())

    proxy = "https://cache-proxy.test.osinfra.cn/download/"

    fail_f = open(r"C:\Users\xxx\Downloads\pkgs_without_tar-master\pkgs_without_tar-master\failed.txt", 'w')
    fail_list = []
    def make_request(proxy_url, official_url):
        try:
            response = requests.get(proxy_url)
            print(f'{response.status_code} {response.url}')
            if response.status_code != 200:
                fail_list.append(f"{response.status_code}  {response.url} {sources_dict[official_url]} {official_url}")
        except Exception as e:
            fail_list.append(f"error {sources_dict[official_url]} {official_url}")
            print(f'error {official_url}')

    num_requests = 50
    interval = 1
    p = 0
    while True:
        start_time = time.time()
        for i in range(num_requests):
            threading.Thread(target=make_request, args=(proxy + sources[p], sources[p],)).start()
            p = p + 1
            if p == len(sources):
                for fail in fail_list:
                    fail_f.write(f"{fail}\n")
                return
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time < interval:
            time.sleep(interval - elapsed_time)
    fail.close()


if __name__ == "__main__":
    test()
