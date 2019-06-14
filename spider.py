#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from bs4 import *
import requests
import time
import random
import re
import os
import datetime
import traceback
import urllib


headerTemp = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "bbs.nga.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
    # "Referer":
    # "Cookie":
}

maxpagenumber = 0
counter = 0


def check_cookie_file():  # 检查cookie是否过期
    try:
        f = open("cookie cache.txt", "r")
    except IOError:
        print("no cache file, creating")
        try:
            f = open("cookie cache.txt", "w")  # 新建文件
            f.close()
            print("creating COMPLETED")
            return 1
        except IOError:
            print("creating ERROR:", traceback.print_exc())
            return 0
    print("cookie file exists")
    f.close()
    originmodifytime = time.localtime(os.stat("cookie cache.txt").st_mtime)
    modifytime = time.strftime("%Y,%m,%d,%H,%M,%S", originmodifytime)
    localtime = time.strftime("%Y,%m,%d,%H,%M,%S", time.localtime())
    time1 = datetime.datetime.strptime(modifytime, "%Y,%m,%d,%H,%M,%S")
    time2 = datetime.datetime.strptime(localtime, "%Y,%m,%d,%H,%M,%S")
    res = time2 - time1
    if res.seconds > 600:  # 游客cookie有效时间10分钟，超过则刷新
        print("stored cookie out of date, refresh")
        return 1


def read_cookie_from_file():  # 从文件读取cookie
    try:
        f = open("cookie cache.txt", "r")
        cookie = f.read()
    except IOError:
        print("read cookie file ERROR:", traceback.print_exc())
        return 0
    print("cookie:", cookie)
    f.close()
    return cookie


def get_cookie():  # 获取新cookie
    time.sleep(random.uniform(1, 2))
    ses = requests.session()
    header = headerTemp.copy()
    header["Referer"] = "https://bbs.nga.cn/thread.php?fid=-7"
    ses.headers = header
    req = ses.get("https://bbs.nga.cn/thread.php?fid=-7")
    checkstr = re.findall(re.compile("lastvisit=.*?;"), req.headers["Set-Cookie"])[0] + " "
    try:
        checkstr += re.findall(re.compile("ngaPassportUid=.*?;"), req.headers["Set-Cookie"])[0] + " "
    except IndexError:
        return 0
    checkstr += re.findall(re.compile("guestJs=.*?;"), req.content.decode('gbk', 'ignore'))[0][:-1]
    try:  # 获取cookie并写入文件
        f = open("cookie cache.txt", "w")
        f.write(checkstr)
        f.close()
    except IOError:
        print("write ERROR:", traceback.print_exc())
    print("get cookie and write COMPLETED")


def read_page(url):  # 读取页面
    global maxpagenumber
    time.sleep(random.uniform(1, 2))
    cookie = read_cookie_from_file()
    if cookie == 0:
        return 0
    ses = requests.session()
    header = headerTemp.copy()
    header["Referer"] = url
    header["Cookie"] = cookie
    ses.headers = header
    req = ses.get(url)
    bs = BeautifulSoup(req.content, "lxml")
    # print(bs)
    print("get page")
    if url != "https://bbs.nga.cn/thread.php?fid=-7":  # 如果访问页面为水区首页
        print("reading:", url)
        try:
            scripts = str(bs.find_all("script", text=re.compile(r"var __PAGE"))[0])  # 读取帖子回复页数
        except IndexError:
            maxpagenumber = 1
            return bs
        print(scripts)
        final = int(re.findall(re.compile(r":(.?),"), scripts)[0])
        print("pages for this topic is:", final)
        maxpagenumber = final
    return bs


def find_title_and_post_date(bs):  # 读取标题与发布时间
    postdate = bs.find("span", id="postdate0").string
    print("postdate:", postdate)
    title = "".join(re.findall(re.compile(r"(.*) NGA玩家社区"), bs.find("title").string))
    print("topic title:", title)
    return title, str(postdate.split(" ", 1)[0])


def find_shadiao(bs):  # 查找首页内有沙雕图内容的标题
    title = bs.find_all("a", class_="topic")
    match_list = ["沙雕图", "傻屌图", "傻吊图", "沙吊图", "沙屌图", "傻雕图"]
    print("match start\n")
    for n in title:
        if any(shadiao in n.string for shadiao in match_list):
            print("MATCH in", n.string)
            print("https://bbs.nga.cn" + n.get("href"), "\n")
            return "https://bbs.nga.cn" + n.get("href")
        else:
            print("no match in", n.string)
            print("https://bbs.nga.cn" + n.get("href"), "\n")
    print("match COMPLETED")
    return 0


def create_folder(title, url, time):  # 新建文件夹
    title = str(title)
    url = str(url)
    if not os.path.exists("Downloads"):  # Downloads文件夹
        print("no Downloads folder, creating")
        try:
            os.mkdir("Downloads")
        except OSError:
            print("creating folder ERROR:", traceback.print_exc())
            return 0
        else:
            print("folder created")

    if not os.path.exists("Downloads/" + time + title):  # 帖子文件夹
        print("no sub folder, creating")
        # 文件名不能包含\/:*?"<>|，在txt内存储
        title = re.sub(re.compile(r"[\\/:*?\"<>|]"), "", title)
        try:
            os.mkdir("Downloads/" + time + title)
        except OSError:
            print(traceback.print_exc())
            return 0
        else:
            print("sub folder created")

    if not os.path.exists("Downloads/" + time + title + "/url.txt"):  # 文本文件用于放置URL
        print("no url text file exist, creating")
        try:
            f = open("Downloads/" + time + title + "/url.txt", "w")
            f.write(url)
            f.close()
        except IOError:
            print("writing ERROR:", traceback.print_exc())
            return 0
        else:
            print("url text file created")
    return "Downloads/" + time + title + "/"


def read_pic_url(bs):  # 读取当前页所有图片URL
    scriptpattern = re.compile(r"url:")
    scripts = bs.find_all("script", text=scriptpattern)
    # print(scripts[-1].string, "\n")
    urlpattern = re.compile(r"url:'(.*?)',name")
    urlgroup = []
    for n in range(len(scripts)):
        urls = re.findall(urlpattern, scripts[n].string)
        print("the No.", n+1, "pic floor")
        for url in urls:
            urlgroup.append("https://img.nga.178.com/attachments/" + url)
            print(url)
        else:
            print()
    return urlgroup


def download_pic(urlgroup, path):  # 下载图片
    print("download start")
    pattern = re.compile(r"-(.*)")
    for url in urlgroup:
        picname = re.findall(pattern, url)
        print("picture name:", picname)
        print("picture url:", url)
        if not os.path.exists(path + str(picname[0])):  # 检查是否重复
            try:
                time.sleep(random.uniform(1, 2))
                urllib.request.urlretrieve(url, path + str(picname[0]))
            except IOError:
                print(traceback.print_exc())
            else:
                print("download COMPLETED\n")
        else:
            print("file exists\n")
    print("all picture for this page download COMPLETED")


def read_topic_and_download(url, path=""):  # 递归顺序读取到帖子页尾
    bs = read_page(url)
    if path == "":
        title, date = find_title_and_post_date(bs)
        path = create_folder(title, url, date)
    if path == 0:
        return
    urlgroup = read_pic_url(bs)
    download_pic(urlgroup, path)
    if "&page=" in url and int(url[-1]) < maxpagenumber:
        print("ready to download page No.", int(url[-1])+1)
        read_topic_and_download(url[:-1] + str(int(url[-1])+1), path)
    else:
        print("all pages download COMPLETED")
        return 
    if maxpagenumber > 1:
        print("ready to download page No.2")
        read_topic_and_download(url + "&page=2", path)


if __name__ == "__main__":
    while True:
        counter += 1
        print("\nThe No.%d loop" % counter)
        cookiestate = check_cookie_file()
        if cookiestate == 1:
            cookie = get_cookie()
            while cookie == 0:
                cookie = get_cookie()
        elif cookiestate == 0:
            continue
        bs = read_page("https://bbs.nga.cn/thread.php?fid=-7")
        if bs == 0:
            continue
        shadiaourl = find_shadiao(bs)
        if shadiaourl != 0:
            read_topic_and_download(shadiaourl)
        print("waiting for next loop (31 seconds later)")
        print("last time:", time.asctime(time.localtime(time.time())))
        time.sleep(31)
    print("exit")
