# coding=utf-8
import urllib
import re
import os
import sys
import time
import thread
import string
import datetime

link = u"http://www.luoo.net/music/"
url = u"http://luoo-mp3.kssws.ks-cdn.com/low/luoo/"

def getDownloadPath():  # 获取下载路径
    if "linux" in sys.platform:
        return u"/etc/luoo/"
    elif "darwin" in sys.platform:
        return u"/Users/Recover/Downloads/luoo/"
    elif "windows" in sys.platform:
        return "C://luoo/"


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    html = unicode(html, "utf-8")
    return html


def getVol(html):  # 获取期刊名字
    regex = r'<span class="vol-title">(.+)</span>'
    vol_regex = re.compile(regex)
    vol_title = re.findall(vol_regex, html)
    return vol_title[0]


def getImg(html):  # 获取图片链接
    regex = r'img src="(http://7xkszy.com2.z0.glb.qiniucdn.com/pics/albums/.+?.jpg)'
    img_regex = re.compile(regex)
    img_list = re.findall(img_regex, html)
    return img_list


def getName(html):  # 获取歌曲名称
    regex = r'<p class="name">(.+)</p>'
    name_regex = re.compile(regex)
    name_list = re.findall(name_regex, html)
    return name_list


def getArtist(html):  # 获取歌手名字
    regex = r'<p class="artist">Artist: (.+)</p>'
    artist_regex = re.compile(regex)
    artist_list = re.findall(artist_regex, html)
    return artist_list


def checkFileName(name):  # 去除歌曲名中的非法字符
    char = '\/:*?"<>|'
    name = [c for c in name]
    for c in name:
        if c in char:
            name.remove(c)
    name = "".join(name)
    return name


def checkSong(song):  # 确保歌曲链接正确
    if urllib.urlopen(song).getcode() != 200:
        song = [c for c in song]
        song.insert(-5, u"0")
        song = "".join(song)
        print(song)
    return song


def progress(count, block_size, total_size):  # 显示下载进度
    per = 100 * count * block_size / total_size
    now = count * block_size / 1024
    total = total_size / 1024
    if now > total:
        now = total
        per = 100
    print "\r%.2f%%  %dkb/%dkb" % (per, now, total),


def download():
    start_vol = raw_input(u"Please enter the starting Vol:")
    start_vol = string.atoi(start_vol)
    end_vol = raw_input(u"Please enter the ending Vol:")
    end_vol = string.atoi(end_vol)
    img_count = 0
    song_count = 0
    img_failed = 0
    song_failed = 0

    if os.path.exists(getDownloadPath()) == False:
        os.makedirs(getDownloadPath())  # 创建下载目录
        
    logFile = open(getDownloadPath() + "log" + unicode(start_vol).zfill(3) + "-" + unicode(end_vol).zfill(3) + ".txt", "a")  # 日志文件
    now = datetime.datetime.now()
    logFile.write("\n\n-----------------" + now.strftime('%Y-%m-%d %H:%M:%S') + "-----------------\n")
    logFile.close()

    for vol_num in range(start_vol, end_vol + 1):
        html = getHtml(link + unicode(vol_num))
        vol_title = getVol(html)  # 期刊名称
        img_list = getImg(html)  # 封面图片链接列表
        name_list = getName(html)  # 歌曲名列表
        artist_list = getArtist(html)  # 艺术家列表

        song_list = [url + u"radio" + unicode(vol_num) + u"/" + unicode(
            song_num) + u".mp3" for song_num in range(1, len(img_list) + 1)]  # 歌曲链接列表

        vol_path = getDownloadPath() + u"VOL." + \
            unicode(vol_num).zfill(3) + " " + vol_title  # 期刊路径

        img_filename = [checkFileName(artist_list[song_list.index(
            song)] + u" - " + name_list[song_list.index(song)] + u" cover.jpg") for song in song_list]  # 图片文件名列表

        img_path = [
            vol_path + u"/" + img_filename[song_list.index(song)] for song in song_list]  # 图片路径列表

        song_filename = [checkFileName(artist_list[song_list.index(
            song)] + u" - " + name_list[song_list.index(song)] + u".mp3") for song in song_list]  # 歌曲文件名列表

        song_path = [
            vol_path + u"/" + song_filename[song_list.index(song)] for song in song_list]  # 歌曲路径列表
            
        if os.path.exists(vol_path) == False:
            os.makedirs(vol_path)  # 根据期刊路径创建目录

        print u"\nDownloading Vol." + unicode(vol_num).zfill(3) + u" " + vol_title

        for i in range(0, len(img_list)):
            for retry in range(4):
                try:
                    print u"\nDownloading " + img_filename[i]
                    urllib.urlretrieve(
                        img_list[i], img_path[i], progress)
                    img_count += 1
                    break
                except Exception, msg:
                    print u"Dowload image error:"
                    print(msg)
                    if retry == 3:
                        print(u"\nImage Error: VOL." + unicode(vol_num).zfill(3) +  u" " + vol_title);
                        print(unicode(i).zfill(2) + u". " + img_filename[i])
                        logFile = open(getDownloadPath() + "log" + unicode(start_vol).zfill(3) + "-" + unicode(end_vol).zfill(3) + ".txt", "a")
                        logFile.write(u"\nImage Error: VOL." + unicode(vol_num).zfill(3) + u" " + vol_title)
                        logFile.write(u" " + unicode(i + 1).zfill(2) + u". " + img_filename[i])
                        logFile.close()
                        img_failed += 1

        for i in range(0, len(song_list)):
            for retry in range(4):
                try:
                    print u"\nDownloading " + song_filename[i]
                    urllib.urlretrieve(
                        checkSong(song_list[i]), song_path[i], progress)
                    song_count += 1
                    break
                except Exception, msg:
                    print u"Dowload song error:"
                    print(msg)
                    if retry == 3:
                        print(u"\nSong Error: VOL." + unicode(vol_num).zfill(3) +  u" " + vol_title);
                        print(unicode(i).zfill(2) + u". " + song_filename[i])
                        logFile = open(getDownloadPath() + "log" + unicode(start_vol).zfill(3) + "-" + unicode(end_vol).zfill(3) + ".txt", "a")
                        logFile.write(u"\nSong Error: VOL." + unicode(vol_num).zfill(3) + u" " + vol_title)
                        logFile.write(u" " + unicode(i + 1).zfill(2) + u". " + song_filename[i])
                        logFile.close()
                        song_failed += 1
        print "\n"
    print(u"Downloaded %d image(s) %d song(s), %d image(s) %d song(s) failed." %
          (img_count, song_count, img_failed, song_failed))

reload(sys)  
sys.setdefaultencoding('utf8')

try:
    startTime = time.time()
    download()
    endTime = time.time()
    print(u"Cost %.2fs." % (endTime - startTime))
except Exception, msg:
    print u"Download error:"
    print(msg)
raw_input(u"\nPress any key to exit.\n")
