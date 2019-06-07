from bs4 import *
import requests
import time
import re

# def run():


def read_page(url):
    ses = requests.session()
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "bbs.nga.cn",
        "Referer": url,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
    }
    ses.headers = header
    req = ses.get(url, headers=header)
    time.sleep(1)
    checkstr = re.findall(re.compile("lastvisit=.*?;"), req.headers["Set-Cookie"])[0]+" "
    checkstr += re.findall(re.compile("ngaPassportUid=.*?;"), req.headers["Set-Cookie"])[0]+" "
    checkstr += re.findall(re.compile("guestJs=.*?;"), req.content.decode('gbk', 'ignore'))[0][:-1]
    ses.headers["Cookie"] = checkstr
    if url == "https://bbs.nga.cn/thread.php?fid=-7":
        url += "&rand=233"
    ses.get(url)
    time.sleep(1)
    req = ses.get(url)
    bs = BeautifulSoup(req.content, "lxml")
    # print(bs)
    return bs


# def find_key_word(bs):


server = "https://bbs.nga.cn"
bs = read_page("https://bbs.nga.cn/thread.php?fid=-7")
title = bs.find_all("a", class_="topic")
match_list = ["沙雕图", "傻屌图", "傻吊图", "沙吊图", "沙屌图", "傻雕图"]
for n in title:
    if any(shadiao in n.string for shadiao in match_list):
        print("MATCH in", n.string, server + n.get("href"), "\n")
    else:
        print("no match in", n.string)

