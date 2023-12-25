import json
import os
import re

showrc_file_path = "d:\\showrc.txt"


def read_file_content(file_path):
    with open(file_path, "r", encoding="gb18030", errors="ignore") as f:
        txt = f.read()
        return txt


def find_value(keywords, origin):
    line_list = origin.split(os.linesep)
    target = ""
    append = False
    for i, line in enumerate(line_list):
        if re.match("-\d+: " + keywords, line) is not None:
            re_words = re.findall("-\d+: " + keywords, line)[0]
            temp_words = line.replace(re_words + " ", "")
            if temp_words != "":
                target += temp_words
            append = True
            continue
        if append:
            if re.match("-\d+: ", line) is not None:
                append = False
            else:
                target += line + os.linesep
    return target


class RpmParser:
    def __init__(self, path=showrc_file_path):
        self.text = read_file_content(path)
        self.arch = "x86_64"
        self.metadata = {}

    def parser(self):
        for _key, _value in self.metadata.items():
            if _value == "":
                print("key {0} parse again".format(_key))
                self.metadata[_key] = find_value(_key, self.text)
            elif _value.startswith("\t"):
                self.metadata[_key] = _value.replace("\t", "")

    def key_value_loader(self):
        line_list = self.text.split("\n")
        temp_value = ""
        keyword = ""
        for line in line_list:
            if re.match("(-13|-20):.*", line) is not None:
                if temp_value != "":
                    self.metadata[keyword] = temp_value.strip()
                    temp_value = ""
                line = line.replace("-13:", "", 1).strip()
                keyword = line.split()[0]
                temp_value += line.replace(keyword, "", 1) + "\n"
            else:
                if keyword != "":
                    temp_value += line + "\n"
        if temp_value != "":
            self.metadata[keyword] = temp_value.strip()

    def dict_writer(self, file_type="json"):
        if file_type == "json":
            if self.metadata:
                with open("rpm_showrc.json", "w", encoding="utf-8", errors="ignore") as f:
                    f.write(json.dumps(self.metadata, indent=4, ensure_ascii=False))
        elif file_type == "yaml" or file_type == "yml":
            if self.metadata:
                with open("rpm_showrc.yaml", "w", encoding="utf-8", errors="ignore") as f:
                    for _key, _value in self.metadata.items():
                        f.write("\"" + _key + "\": \"" + _value + "\"")


if __name__ == '__main__':
    rpm_parser = RpmParser()
    rpm_parser.key_value_loader()
    rpm_parser.parser()
    rpm_parser.dict_writer()
