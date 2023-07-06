import os
import subprocess


def test():
    sources_dict = {}
    p_path = r"/root/pkgs_without_tar/pkgs"
    pkgs = os.listdir(p_path)
    for pkg in pkgs:
        f_path = os.path.join(p_path, pkg)
        if not os.path.isdir(f_path):
            continue
        files = os.listdir(f_path)
        for f_name in files:
            if f_name.endswith(".spec"):
                spec_path = os.path.join(f_path, f_name)
                with open(f"/root/tmp/spec/{f_name}", 'w') as f:
                    subprocess.run(['rpmspec', '-P', spec_path], stdout=f)
                sources = subprocess.run(['spectool', '-S', f"/root/tmp/spec/{f_name}"], stdout=subprocess.PIPE).stdout.decode().splitlines()
                for source in sources:
                    source = source.split(":", 1)[1].strip()
                    if source.startswith("http:") or source.startswith("https:"):
                        sources_dict[source] = f_name
    # print(len(sources))
    # for i in range(11001):
    #     print(sources[i])

    with open(r"/root/pkgs_without_tar/pkgs/sources_dict.txt", 'w') as f:
        for source in sources_dict:
            f.write(sources_dict[source] + " " + source + "\n")


if __name__ == "__main__":
    test()