# -*- coding: utf-8 -*-

import time
from threading import Thread
from urllib import parse
from urllib.parse import urljoin

import chardet
import requests
from bs4 import BeautifulSoup
from dingtalkchatbot.chatbot import DingtalkChatbot
from selenium import webdriver

global pageURL
global localList
global historySet
global browser
global domainName
global xiaoding
# 初始化机器人小丁
webhook = 'https://oapi.dingtalk.com/robot/send?access_token=3f69bd111a27ad41e6b609acb7b68d1f862d795c331840aa0d9a5abb9fbde223'  # 填写你自己创建的机器人
xiaoding = DingtalkChatbot(webhook)
localList = []
historySet = set()
browser = webdriver.Chrome()


# 不显示浏览器窗口的自动化爬取
def zidonghua_html_noproxy(url):
    browser.get(url)
    return browser.page_source


# 获取html文档
def get_html(object):
    response = requests.get(object['cur'])
    if response.status_code != 200:

        xiaoding.send_text(msg='官网出现死链==> ' + object['cur'] + ' 源网页==> ' + object['refer'],is_at_all=True)  # Text消息@所有人


    else:
        return BeautifulSoup(zidonghua_html_noproxy(object['cur']), 'lxml')


def send_url_verification(object):
    # 只扫描自己的域名
    if object['cur'].find(domainName) != -1:

        soup = get_html(object)
        aList = soup.select("a[href]")
        linkList = list()

        for a in aList:
            href_ = a.attrs['href']
            if href_ and href_[0:1] != '#':
                ym = has_ym(pageUrl, href_)
                obj = {}
                obj['refer'] = object['cur']
                obj['cur'] = ym
                linkList.append(obj)

        # 對linkList 去重
        linkList = _remove_duplicate(linkList)
        localList.extend(linkList)

        #對localList去重
        zz = _remove_duplicate(localList)
        localList.clear()
        localList.extend(zz)


        for object_ in linkList:
            if object_['cur'] not in historySet:
                historySet.add(object_['cur'])
                send_url_verification(object_)


def has_ym(pageUrl, url):
    if url.find(pageUrl) == -1 and url.find('http') == -1:
        url = pageUrl + url

    return url


def _remove_duplicate( dict_list):
    seen = set()
    new_dict_list = []
    for dict in dict_list:
        t_dict = {'cur': dict['cur']}
        t_tup = tuple(t_dict.items())
        if t_tup not in seen:
            seen.add(t_tup)
            new_dict_list.append(dict)
    return new_dict_list





if __name__ == '__main__':
    # domainName = 'www.cyzxs.cn'
    domainName = 'www.cyzxn.cn'
    pageUrl = 'http://' + domainName + '/'  # 需要查询的页面
    object = {}
    object['refer'] = ''
    object['cur'] = pageUrl
    lis = send_url_verification(object)

    browser.quit()

    print("退出程序")
