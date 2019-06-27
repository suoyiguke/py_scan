# -*- coding: utf-8 -*-
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

import logger
log = logger.logger()
log.debug('=================扫描程序开始==========================')
sys.setrecursionlimit(1000000)

import requests
import yaml
from bs4 import BeautifulSoup
from dingtalkchatbot.chatbot import DingtalkChatbot
from gevent import os
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

global pageURL
global localList
global historySet
global browser
global xiaoding
global ymlFile
global url
global access_token

if 'scan_url' in os.environ and  'scan_access_token' in os.environ:
    url = os.environ['scan_url']
    access_token = os.environ['scan_access_token']
else:
    with open('./config.yml', 'r', encoding="utf-8") as f:
        ymlFile = yaml.load(f.read(), Loader=yaml.FullLoader)
    url = ymlFile['scan_url']
    access_token = ymlFile['scan_access_token']

pageUrl = 'http://{url}/'.format(url=url)  # 需要查询的页面

# 初始化机器人小丁
webhook = 'https://oapi.dingtalk.com/robot/send?access_token={access_token}'.format(access_token=access_token)  # 填写你自己创建的机器人
xiaoding = DingtalkChatbot(webhook)
localList = []
historySet = set()


try:
    browser = webdriver.Remote(
        command_executor="http://chrome:4444/wd/hub",
        desired_capabilities=DesiredCapabilities.CHROME
    )
except BaseException as err:
    log.error(err)
    browser = webdriver.Chrome()

finally:
    log.error('请检查好Chrome环境！')



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
    if object['cur'].find(url) != -1:
        log.debug('扫描'+object['cur']+'中...'+'它的来源是'+ object['refer'])
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


def main():
    object = {}
    object['refer'] = ''
    object['cur'] = pageUrl
    lis = send_url_verification(object)
    # browser.quit()
    log.debug('=================扫描程序结束==========================')



if __name__ == '__main__':
    sched = BlockingScheduler()
    #4小时
    main()
    sched.add_job(main,'interval',  seconds=14400)
    sched.start()

