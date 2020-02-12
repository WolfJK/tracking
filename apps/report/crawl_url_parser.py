# -*- coding: utf8 -*-
from __future__ import unicode_literals, print_function
import traceback
import requests
import re
import urllib2

platform = {
    "babyschool": "1010",
    "babytree": "1001",
    "baobao": "1019",
    "bozhong": "1018",
    "ci123": "1008",
    "dangmala": "1124",  # NO
    "drcuiyutao": "1122",
    "eyzhs": "1017",  # NO
    "haoyunbang": "1020",
    "haoyunma": "1105",
    "hibb": "1127",  # NO
    "ibabyzone": "1117",  # NO
    "ibabyzonepc": "1011",
    "ihealthbaby": "1109",  # NO
    "iyaya": "1016",  # NO
    "j": "1125",  # NO
    "jingqizhushou": "1115",  # NO
    "ladybirdedu": "1114",  # NO
    "lmbang": "1006",
    "lamabang": "1006",
    "mama": "1005",
    "mamashai": "1119",  # NO
    "mami": "1104",  # NO
    "manyuemama": "1112",  # NO
    "mimi518": "1012",
    "mmbang": "1007",
    "oursapp": "1120",  # NO
    "pcbaby": "1004",
    "qbaobei": "1013",  # NO
    "qbb6": "1110",
    "qqbaobao": "1021",  # NO
    "qubaobei": "1113",
    "mamashequ": "1113",
    "sina": "1009",  # NO
    "tsys91": "1118",  # NO
    "utanbaby": "1015",  # NO
    "yaolan": "1003",  # NO
    "yeemiao": "1121",  # NO
    "yoloho": "1107",
    "youbaobao": "1102",  # NO
    "seeyouyima": "1102",
    "youyou360": "1103",  # NO
    "yuerbao": "1116",
    "yunbaober": "1126",  # NO
    "yunfubannv": "1108",  # NO
    "zhilehuo": "1111",  # NO
    "weibo": "3002",
    "zhihu": "5002",
}
socials = [
    "3002",
    "5002"
]


def html(url, page=1):
    try:
        resp = requests.get(url)
        text = resp.text.replace(" ", "")
    except:
        traceback.print_exc()
        if page < 4:  # 允许抓取错误重试次
            text = html(url, page + 1)
        else:
            text = ""
    return text


def rule(domain_name, url):
    category_id = post_id = ""
    channel = "2"
    platform_id = platform[domain_name]
    if domain_name == "babyschool":
        post_id = re.findall("thread-(\d+)", url)[0] if re.findall("thread-(\d+)", url) else ""
    elif domain_name == "babytree":
        if re.findall("(\w+)\/topic_(\d+)", url):
            category_id, post_id = re.findall("(\w+)\/topic_(\d+)", url)[0]
            post_id = "topic_" + post_id
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
        elif re.findall("[^a-zA-Z0-9_]id\=(\d+)", url):
            post_id = re.findall("[^a-zA-Z0-9_]id\=(\d+)", url)[0]
            platform_id = "1113"
    elif domain_name == "drcuiyutao":
        post_id = re.findall("[^a-zA-Z0-9_]id=(\d+)", url)[0] if re.findall("[^a-zA-Z0-9_]id=(\d+)", url) else ""
    elif domain_name == "haoyunma":
        post_id = re.findall("[^a-zA-Z0-9_]id=(\d+)", url)[0] if re.findall("[^a-zA-Z0-9_]id=(\d+)", url) else ""
    elif domain_name == "haoyunbang":
        post_id = re.findall("info\/(\w+)", url)[0] if re.findall("info\/(\d+)", url) else ""
    elif domain_name == "ibabyzonepc":
        post_id = re.findall("topic\-(\d+)", url)[0] if re.findall("topic\-(\d+)", url) else ""
    elif domain_name == "ladybirdedu":
        post_id = re.findall("[^a-zA-Z0-9_]id=(\d+)", url)[0] if re.findall("[^a-zA-Z0-9_]id=(\d+)", url) else ""
    elif domain_name == "lamabang" or domain_name == "lmbang":
        post_id = re.findall("[^a-zA-Z0-9_]id\-(\d+)", url)[0] if re.findall("[^a-zA-Z0-9_]id\-(\d+)", url) else ""
    elif domain_name == "mama":
        if re.findall("topic\/(\d+)", url):
            post_id = re.findall("topic\/(\d+)", url)[0]
        elif re.findall("tlq\/(\d+)", url):
            post_id = re.findall("tlq\/(\d+)", url)[0]
        elif re.findall("ask\/q(\d+)", url):
            post_id = re.findall("ask\/q(\d+)", url)[0]
            post_id = "q" + post_id
            channel = "1"
    elif domain_name == "mimi518":
        category_id, post_id = re.findall("(\d+)\/topic\-(\d+)", url)[0] if re.findall("(\d+)\/topic\-(\d+)",
                                                                                       url) else ""
    elif domain_name == "mmbang":
        if re.findall("bang\/(\d+)\/(\d+)", url):
            category_id, post_id = re.findall("bang\/(\d+)\/(\d+)", url)[0]
        if re.findall("bang\/(\d+)", url):
            post_id = re.findall("bang\/(\d+)", url)[0]
        elif re.findall("ask\/q(\d+)", url):
            post_id = re.findall("ask\/q(\d+)", url)[0]
            channel = "1"
    elif domain_name == "pcbaby":
        if re.findall("topic\-(\d+)", url):
            post_id = re.findall("topic\-(\d+)", url)[0]
            post_id = "topic-" + post_id
        elif re.findall("question\/(\d+)", url):
            post_id = re.findall("question\/(\d+)", url)[0]
            channel = "1"
    elif domain_name == "qbb6":
        if "qbb6.com/post/community/" in url:
            text = html(url)
            post_id = re.findall("pid=(\d+)", text)[0] if re.findall("pid=(\d+)", text) else ""
    elif domain_name == "seeyouyima":
        if re.findall("detail\/(\d+)", url):
            post_id = re.findall("detail\/(\d+)", url)[0]
    elif domain_name == "mamashequ":
        post_id = re.findall("[^a-zA-Z0-9_]id=(\d+)", url)[0] if re.findall("[^a-zA-Z0-9_]id=(\d+)", url) else ""
    elif domain_name == "yoloho":
        post_id = re.findall("topicId=(\d+)", url)[0] if re.findall("topicId=(\d+)", url) else ""
    elif domain_name == "yuerbao":
        post_id = re.findall("post_id=(\d+)", url)[0] if re.findall("post_id=(\d+)", url) else ""
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
    url_replace = url.replace("//", ".")
    for domain_name in url_replace.split("."):
        if platform.get(domain_name) is not None:
            platform_id, post_id = rule(domain_name, url)
            print(platform_id, "_____", post_id)
            return platform_id, post_id
    return "", ""


if __name__ == "__main__":
    parse_url("https://weibo.com/6180424229/H9Yjzr5H5")
    parse_url("https://www.qbb6.com/post/community/r08LEcbAqgC")
    parse_url("https://h5new.haoyunma.com/topic/share?id=20265055&from=singlemessage&isappinstalled=0")
    parse_url(
        "https://forum-h5.yoloho.com/wap/topic/index?topicId=1477990&dayima_signature=87f25ae848ea7bd4a040df459068189e&from=singlemessage&isappinstalled=0")
    parse_url(
        "http://www.ladybirdedu.com/pregnotice/yunmabang/index.php?id=23244194&is_share=1&user_id=0&time=1581315409&from=singlemessage&isappinstalled=0")
    parse_url("http://www.mama.cn/ask/q18184182-p1.html")
    parse_url("https://bbs.pcbaby.com.cn/topic-21950965-3.html")
    parse_url("http://www.babytree.com/community/yuer/topic_91087946_11322.html")
