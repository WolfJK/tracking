# -*- coding: utf8 -*-
# url平台解析

from __future__ import unicode_literals, print_function
import re


platform = {
    "babyschool": "1010",
    "babytree": "1001",
    "baobao": "1019",
    "bozhong": "1018",
    "ci123": "1008",
    "dangmala": "1124",
    "drcuiyutao": "1122",
    "eyzhs": "1017",
    "haoyunbang": "1020",
    "haoyunma": "1105",
    "hibb": "1127",
    "ibabyzone": "1117",
    "ibabyzonepc": "1011",
    "ihealthbaby": "1109",
    "iyaya": "1016",
    "j": "1125",
    "jingqizhushou": "1115",
    "ladybirdedu": "1114",
    "lmbang": "1006",
    "mama": "1005",
    "mamashai": "1119",
    "mami": "1104",
    "manyuemama": "1112",
    "mimi518": "1012",
    "mmbang": "1007",
    "oursapp": "1120",
    "pcbaby": "1004",
    "qbaobei": "1013",
    "qbb6": "1110",
    "qqbaobao": "1021",
    "qubaobei": "1113",
    "sina": "1009",
    "tsys91": "1118",
    "utanbaby": "1015",
    "yaolan": "1003",
    "yeemiao": "1121",
    "yoloho": "1107",
    "youbaobao": "1102",
    "seeyouyima": "1102",
    "youyou360": "1103",
    "yuerbao": "1116",
    "yunbaober": "1126",
    "yunfubannv": "1108",
    "zhilehuo": "1111",
    "weibo": "3002",
    "zhihu": "5002",
}
socials = [
    "3002",
    "5002"
]


def rule(domain_name, url):
    category_id, post_id = "", ""
    channel = "2"
    platform_id = platform[domain_name]
    if domain_name == "babyschool":
        post_id = re.findall("thread-(\d+)", url)[0] if re.findall("thread-(\d+)", url) else ""
    elif domain_name == "babytree":
        if re.findall("(\w+)\/topic_(\d+)", url):
            category_id, post_id = re.findall("(\w+)\/topic_(\d+)", url)[0]
        elif re.findall("qid\~(\d+)", url):
            post_id = re.findall("qid~(\d+)", url)[0]
            channel = "1"
        elif re.findall("detail\/(\d+)", url):
            post_id = re.findall("detail\/(\d+)", url)[0]
            channel = "1"
    elif domain_name == "baobao":
        if re.findall("article\/(\w+)\.html", url):
            post_id = re.findall("article\/(\w+)\.html", url)[0]
        elif re.findall("question\/(\w+)\.html", url):
            post_id = re.findall("question\/(\w+)\.html", url)[0]
            channel = "1"
        else:
            post_id = ""
    elif domain_name == "bozhong":
        post_id = re.findall("thread-(\d+)", url)[0] if re.findall("thread-(\d+)", url) else ""
    elif domain_name == "ci123":
        if re.findall("post\/(\d+)", url):
            post_id = re.findall("post\/(\d+)", url)[0]
        elif re.findall("show\/(\d+)", url):
            post_id = re.findall("show\/(\d+)", url)[0]
            channel = "1"
        elif re.findall("id\=(\d+)", url):
            post_id = re.findall("id\=(\d+)", url)[0]
            platform_id = "1113"
    elif domain_name == "haoyunbang":
        post_id = re.findall("info\/(\w+)", url)[0] if re.findall("info\/(\d+)", url) else ""
    elif domain_name == "ibabyzonepc":
        post_id = re.findall("topic\-(\d+)", url)[0] if re.findall("topic\-(\d+)", url) else ""
    elif domain_name == "lamabang" or domain_name == "lmbang":
        post_id = re.findall("id\-(\d+)", url)[0] if re.findall("id\-(\d+)", url) else ""
    elif domain_name == "mama":
        if re.findall("topic\/(\d+)", url):
            post_id = re.findall("topic\/(\d+)", url)[0]
        elif re.findall("tlq\/(\d+)", url):
            post_id = re.findall("tlq\/(\d+)", url)[0]
        elif re.findall("ask\/p(\d+)", url):
            post_id = re.findall("ask\/p(\d+)", url)[0]
            channel = "1"
    elif domain_name == "mimi518":
        category_id, post_id = re.findall("(\d+)\/topic\-(\d+)", url)[0] if re.findall("(\d+)\/topic\-(\d+)",
                                                                                       url) else ""
    elif domain_name == "mmbang":
        if re.findall("bang\/(\d+)\/(\d+)", url):
            category_id, post_id = re.findall("bang\/(\d+)\/(\d+)", url)[0]
        elif re.findall("ask\/q(\d+)", url):
            post_id = re.findall("ask\/q(\d+)", url)[0]
            channel = "1"
    elif domain_name == "pcbaby":
        if re.findall("topic\-(\d+)", url):
            post_id = re.findall("topic\-(\d+)", url)[0]
        elif re.findall("question\/(\d+)", url):
            post_id = re.findall("question\/(\d+)", url)[0]
            channel = "1"
    elif domain_name == "seeyouyima":
        if re.findall("detail\/(\d+)", url):
            post_id = re.findall("detail\/(\d+)", url)[0]
    elif domain_name == "weibo":
        post_id = url.split("?")[0].split("/")[-1]
    elif domain_name == "zhihu":
        if re.findall("question\/(\d+)", url):
            post_id = re.findall("question\/(\d+)", url)[0]
            channel = "1"
        elif re.findall("q\/(\d+)", url):
            post_id = re.findall("q\/(\d+)", url)[0]
            channel = "2"
    if post_id != "" and platform_id not in socials:
        post_id = "{}:{}:{}".format(platform_id, channel, post_id)
    return platform_id, post_id


def parse_url(url):
    url = url.replace("//", ".")
    for domain_name in url.split("."):
        if platform.get(domain_name) is not None:
            platform_id, post_id = rule(domain_name, url)
            # print(platform_id, "_____", post_id)
            return platform_id, post_id
    return "", ""


if __name__ == "__main__":
    parse_url("https://weibo.com/6180424229/H9Yjzr5H5")
