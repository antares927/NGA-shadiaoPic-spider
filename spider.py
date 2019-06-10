from bs4 import *
import requests
import time
import random
import re
import os
import sys
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


def check_cookie_file():
    try:
        f = open("cookie cache.txt", "r")  # 检查cookie缓存文件
    except IOError:
        print("no cache file, creating")
        try:
            f = open("cookie cache.txt", "w")  # 新建文件
            f.close()
            print("creating completed")
            return 1
        except IOError:
            print("creating error:", traceback.print_exc())
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


def read_cookie_from_file():
    try:
        f = open("cookie cache.txt", "r")  # 从文件读取cookie
        cookie = f.read()
    except IOError:
        print("read cookie file error:", traceback.print_exc())
        return 0
    print("cookie:", cookie)
    f.close()
    return cookie


def get_cookie():
    time.sleep(random.uniform(1, 2))
    ses = requests.session()
    header = headerTemp
    header["Referer"] = "https://bbs.nga.cn/thread.php?fid=-7"
    ses.headers = header
    req = ses.get("https://bbs.nga.cn/thread.php?fid=-7")
    checkstr = re.findall(re.compile("lastvisit=.*?;"), req.headers["Set-Cookie"])[0] + " "
    checkstr += re.findall(re.compile("ngaPassportUid=.*?;"), req.headers["Set-Cookie"])[0] + " "
    checkstr += re.findall(re.compile("guestJs=.*?;"), req.content.decode('gbk', 'ignore'))[0][:-1]
    try:  # 获取cookie并写入文件
        f = open("cookie cache.txt", "w")
        f.write(checkstr)
        f.close()
    except IOError:
        print("write error:", traceback.print_exc())
    print("get cookie and write completed")


def read_page(url):
    time.sleep(random.uniform(1, 2))
    if url == "https://bbs.nga.cn/thread.php?fid=-7":  # 如果访问页面为水区首页
        url += "&rand=233"
    cookie = read_cookie_from_file()
    if cookie == 0:
        return 0
    ses = requests.session()
    header = headerTemp
    header["Referer"] = url
    header["Cookie"] = cookie
    ses.headers = header
    req = ses.get(url)
    bs = BeautifulSoup(req.content, "lxml")
    # print(bs)
    print("get page")
    return bs


def find_post_date(bs):
    postdate = bs.find("span", id="postdate0").string
    print("postdate:", postdate)
    return str(postdate.split(" ", 1)[0])


def find_shadiao(bs):
    title = bs.find_all("a", class_="topic")
    match_list = ["沙雕图", "傻屌图", "傻吊图", "沙吊图", "沙屌图", "傻雕图"]
    print("match start\n")
    for n in title:
        if any(shadiao in n.string for shadiao in match_list):
            print("MATCH in", n.string)
        else:
            print("no match in", n.string)
        print("https://bbs.nga.cn" + n.get("href"), "\n")
    print("match completed")


def create_folder(title, url, time):
    title = str(title)
    url = str(url)
    if not os.path.exists("Downloads"):
        print("no Downloads folder, creating")
        try:
            os.mkdir("Downloads")
        except OSError:
            print("creating folder error:", traceback.print_exc())
            return 0
        else:
            print("folder created")

    if not os.path.exists("Downloads/" + time + title):
        print("no sub folder, creating")
        #  文件名不能包含\/:*?"<>|，在txt内存储
        title = re.sub(re.compile(r"[\\/:*?\"<>|]"), "", title)
        try:
            os.mkdir("Downloads/" + time + title)
        except OSError:
            print(traceback.print_exc())
            return 0
        else:
            print("sub folder created")

    if not os.path.exists("Downloads/" + time + title + "/url.txt"):
        print("no url text file exist, creating")
        try:
            f = open("Downloads/" + time + title + "/url.txt", "w")
            f.write(url)
            f.close()
        except IOError:
            print("writing error:", traceback.print_exc())
            return 0
        print("url text file created")
    return "Downloads/" + time + title + "/"


def read_pic_url(bs):
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


def download_pic(urlgroup, path):
    print("download start")
    pattern = re.compile(r"-(.*)")
    for url in urlgroup:
        picname = re.findall(pattern, url)
        print("picture name:", picname)
        print("picture url:", url)
        time.sleep(random.uniform(1, 2))
        try:
            urllib.request.urlretrieve(url, path + "".join(picname))
        except IOError:
            print(traceback.print_exc())
        else:
            print("download completed\n")
    print("all picture download completed")


if __name__ == '__main__':
    a = check_cookie_file()
    if a == 1:
        get_cookie()
    elif a == 0:
        sys.exit(0)
    # bs = read_page("https://bbs.nga.cn/thread.php?fid=-7")
    bs = read_page("https://bbs.nga.cn/read.php?tid=17524666")
    if bs == 0:
        sys.exit(0)
    # find_shadiao(bs)
    path = create_folder("谁来ps个赛博朋克2077沙雕图？", "https://bbs.nga.cn/read.php?tid=17524666", find_post_date(bs))
    urlgroup = read_pic_url(bs)
    download_pic(urlgroup, path)
