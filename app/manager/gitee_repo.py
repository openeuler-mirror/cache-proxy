import base64
import json
import os.path

import requests


def get_repos():
    access_token = "1d0aefc1bb53b861d81115a696835cc4"
    repo_url = "https://gitee.com/api/v5/orgs/src-openeuler/repos?access_token=1d0aefc1bb53b861d81115a696835cc4&type=all&page=1&per_page=100"
    response = requests.get(repo_url)
    repo_mess = json.loads(response.text)
    repo_list = []
    spec_list = {}
    for repo_info in repo_mess:
        if 'name' in repo_info:
            repo_list.append(repo_info['name'])
    for repo in repo_list:
        tree_url = f"https://gitee.com/api/v5/repos/src-openeuler/{repo}/git/trees/master?access_token=1d0aefc1bb53b861d81115a696835cc4"
        response = requests.get(tree_url)
        tree_mess = json.loads(response.text)
        for item in tree_mess['tree']:
            if item['path'].endswith(".spec"):
                spec_list[item["url"]] = repo
                break
    for spec_url, repo in spec_list.items():
        spec_url = spec_url + "?access_token=1d0aefc1bb53b861d81115a696835cc4"
        response = requests.get(spec_url)
        spec_mess = json.loads(response.text)
        content_base64 = spec_mess['content']
        content = base64.b64decode(content_base64).decode('utf-8')
        with open(os.path.join("C:\\tmp", repo+".spec"), 'w', encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    get_repos()