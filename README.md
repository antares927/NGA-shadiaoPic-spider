# NGA-shadiaoPic-spider
本软件用于收集NGA大漩涡沙雕图

## 原理
每隔31秒读取一次水区首页，寻找标题中带“沙雕图”及其他类似关键词的标题，若匹配则进入下载流程，在程序所在目录下创建Downloads文件夹用于储存图片，每个匹配的帖子拥有专有文件夹，命名与帖子标题相同，所有图片直接下载进入子文件夹

## 使用说明
1. 在Chrome或Firefox中登录自己的NGA账号
2. 运行`spider.py`

或

1. 在Chrome中登录自己的NGA账号
2. 运行`spider_ForConvertToEXE.exe`

**报错说明**
1. No supported browser found (Chrome or Firefox)  
    Browsercookie库仅支持Chrome与Firefox
2. Cookie invalid  
    账号未登录

### Windows
**注：因为在使用pyinstaller转换`spider.py`后执行文件时在import browsercookie库时出现了无法解决的问题，抛弃了browsercookie库用直接解密cookie文件的方法重写了方法，作者电脑上只有Chrome（也懒得去测试Firefox），所以exe文件仅支持Chrome浏览器**

从release内下载并运行`spider_ForConvertToEXE.exe`即可，通过`Ctrl+C`或直接关闭窗口以终止程序

## 免责声明
本程序仅供爱好交流使用，对程序与源码的任何魔改造成的后果本人概不负责
