#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import win32crypt
from bs4 import *
import requests
import time
import random
import re
import os
import traceback
import urllib
import sqlite3

maxpagenumber = 0
counter = 0
cookies = 0


def read_page(url):  # 读取页面
    global maxpagenumber
    time.sleep(random.uniform(1, 2))
    response = requests.get(url, cookies=cookies)
    bs = BeautifulSoup(response.content, "lxml")
    print("Get page")
    print("Reading:", url)
    try:
        scripts = str(bs.find_all("script", text=re.compile(r"var __PAGE"))[0])  # 读取帖子回复页数
    except IndexError:
        maxpagenumber = 1
        return bs
    print(scripts)
    final = int(re.findall(re.compile(r":(.?),"), scripts)[0])
    print("Pages for this topic is:", final)
    maxpagenumber = final
    return bs


def find_title_and_post_date(bs):  # 读取标题与发布时间
    postdate = bs.find("span", id="postdate0").string
    print("Postdate:", postdate)
    title = "".join(re.findall(re.compile(r"(.*) NGA玩家社区"), bs.find("title").string))
    print("Topic title:", title)
    return title, str(postdate.split(" ", 1)[0])


def find_shadiao(bs):  # 查找首页内有沙雕图内容的标题
    title = bs.find_all("a", class_="topic")
    match_list = ["沙雕图", "傻屌图", "傻吊图", "沙吊图", "沙屌图", "傻雕图"]
    print("Match start\n")
    for n in title:
        if any(shadiao in n.string for shadiao in match_list):
            print("MATCH in", n.string)
            print("https://bbs.nga.cn" + n.get("href"), "\n")
            return "https://bbs.nga.cn" + n.get("href")
        else:
            print("No match in", n.string)
            print("https://bbs.nga.cn" + n.get("href"), "\n")
    print("Match COMPLETED")
    return 0


def create_folder(title, url, time):  # 新建文件夹
    title = str(title)
    url = str(url)
    if not os.path.exists("Downloads"):  # Downloads文件夹
        print("No Downloads folder, creating")
        try:
            os.mkdir("Downloads")
        except OSError:
            print("Creating folder ERROR:", traceback.print_exc())
            return 0
        else:
            print("Folder created")

    if not os.path.exists("Downloads/" + time + title):  # 帖子文件夹
        print("No sub folder, creating")
        # 文件名不能包含\/:*?"<>|，在txt内存储
        title = re.sub(re.compile(r"[\\/:*?\"<>|]"), "", title)
        try:
            os.mkdir("Downloads/" + time + title)
        except OSError:
            print(traceback.print_exc())
            return 0
        else:
            print("Sub folder created")

    if not os.path.exists("Downloads/" + time + title + "/url.txt"):  # 文本文件用于放置URL
        print("No url text file exist, creating")
        try:
            f = open("Downloads/" + time + title + "/url.txt", "w")
            f.write(url)
            f.close()
        except IOError:
            print("Writing ERROR:", traceback.print_exc())
            return 0
        else:
            print("Url text file created")
    return "Downloads/" + time + title + "/"


def read_pic_url(bs):  # 读取当前页所有图片URL
    scriptpattern = re.compile(r"url:")
    scripts = bs.find_all("script", text=scriptpattern)
    # print(scripts[-1].string, "\n")
    urlpattern = re.compile(r"url:'(.*?)',name")
    urlgroup = []
    for n in range(len(scripts)):
        urls = re.findall(urlpattern, scripts[n].string)
        print("The No.", n+1, "pic floor")
        for url in urls:
            urlgroup.append("https://img.nga.178.com/attachments/" + url)
            print(url)
        else:
            print()
    return urlgroup


def download_pic(urlgroup, path):  # 下载图片
    print("Download start")
    pattern = re.compile(r"-(.*)")
    for url in urlgroup:
        picname = re.findall(pattern, url)
        print("Picture name:", picname)
        print("Picture url:", url)
        if not os.path.exists(path + str(picname[0])):  # 检查是否重复
            try:
                time.sleep(random.uniform(1, 2))
                urllib.request.urlretrieve(url, path + str(picname[0]))
            except IOError:
                print(traceback.print_exc())
            else:
                print("Download COMPLETED\n")
        else:
            print("File exists\n")
    print("All picture for this page download COMPLETED")


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
        print("Ready to download page No.", int(url[-1])+1)
        read_topic_and_download(url[:-1] + str(int(url[-1])+1), path)
    else:
        print("All pages download COMPLETED")
        return 
    if maxpagenumber > 1:
        print("Ready to download page No.2")
        read_topic_and_download(url + "&page=2", path)


if __name__ == "__main__":
    cookie_file = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data\Default\Cookies') 
    if not os.path.exists(cookie_file):
        print('Cookies file not exist!')
        time.sleep(300)
    con = sqlite3.connect(cookie_file)
    sql = 'select host_key, name, encrypted_value from cookies where host_key like "%nga.178.com%"'
    cur = con.cursor()
    fetch = cur.execute(sql).fetchall()
    cookies = {name: win32crypt.CryptUnprotectData(encrypted_value)[1].decode() for host_key, name, encrypted_value in
               fetch}

    while True:
        counter += 1
        print("\nThe No.%d loop" % counter)

        response = requests.get("https://bbs.nga.cn/thread.php?fid=-7", cookies=cookies)
        if not response.ok:
            print("Cookie invalid")
            time.sleep(300)
            continue
        else:
            print("Loading NGA succeeded")

        bs = BeautifulSoup(response.content, "lxml")
        shadiaourl = find_shadiao(bs)
        if shadiaourl != 0:
            read_topic_and_download(shadiaourl)
        print("Waiting for next loop (31 seconds later)")
        print("Last time:", time.asctime(time.localtime(time.time())))
        time.sleep(31)
    print("Exit")
