import os
import threading

import requests


def get_source0():
    result = []
    spec_dir = "C:\\tmp"
    lists = os.listdir(spec_dir)
    # print(lists)
    for spec_name in lists:
        if spec_name.endswith(".spec"):
            with open(os.path.join(spec_dir, spec_name), 'r', encoding="utf-8") as f:
                lines = f.readlines()
                name = ""
                version = ""
                source0 = ""
                for line in lines:
                    if line.startswith('Name:'):
                        name = line.split()[-1]
                    if line.startswith('Version:'):
                        version = line.split()[-1]
                    if line.startswith('Source0:') or line.startswith('Source:'):
                        source0 = line.split()[-1].replace("%{name}", name).replace("%{version}", version)
                    if name and version and source0:
                        # print(f"{spec_name} source0:{source0}")
                        result.append(source0)
                        break
    return result


def make_request(url):
    response = requests.get(url, allow_redirects=True)
    print(response.url)


def download():
    urls = get_source0()
    threads = []
    for url in urls:
        url = "http://127.0.0.1:5000/download/" + url
        t = threading.Thread(target=make_request, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    # for name in get_source0():
    #     print(name)
    download()