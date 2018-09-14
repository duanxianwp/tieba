# -*- coding: utf-8 -*-
import re

import scrapy
from bs4 import BeautifulSoup
from baidumail.items import BaidumailItem


class MailSpider(scrapy.Spider):
    name = 'mail'
    mail_regx = r'[0-9a-zA-Z._]+@[0-9a-zA-Z._]+\.[0-9a-zA-Z._]+'
    mail_pat = re.compile(mail_regx)
    qq_regx = r'[1-9]\d{4,10}'
    qq_pat = re.compile(qq_regx)
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['http://tieba.baidu.com/']
    school_list = [
        '北京院校', '山东院校', '江苏院校', '四川院校', '湖北院校', '河北院校', '安徽院校',
        '陕西院校', '浙江院校', '辽宁院校', '湖南院校', '福建院校', '江西院校', '重庆院校',
        '广东院校', '河南院校', '山西院校', '上海院校', '黑龙江院校', '天津院校', '吉林院校',
        '广西院校', '云南院校', '甘肃院校', '内蒙古院校', '贵州院校', '海南院校', '新疆院校',
        '宁夏院校', '港澳台院校', '海外院校', '青海院校', '西藏院校', '学校话题', '校园青春'
    ]
    # school_list = [
    #     '北京院校'
    # ]
    # 获取院校名字
    get_school = 'http://tieba.baidu.com/f/index/forumpark?cn={}&ci=0&pcn={}&pci=0&ct=1&st=new&pn={}'
    # 获取院校精品帖
    enter_school = 'http://tieba.baidu.com/f?kw={}&ie=utf-8&tab=good&cid=&pn={}'

    # 获取每个省份的学校
    def start_requests(self):
        for school in self.school_list:
            yield scrapy.Request(url=self.get_school.format(school, '高等学校', 1), callback=self.parse_school)

    def parse_school(self, response):
        soup = self.get_soup(response)
        bas = soup.select('p.ba_name')
        schools = list(map(lambda sh: sh.get_text(), bas))
        for school in schools:
            yield scrapy.Request(url=self.enter_school.format(school, '0'), callback=self.parse_jingpin)
        next = soup.select_one('div.pagination > a.next')
        if next is not None:
            yield scrapy.Request(url=self.start_urls[0] + self.handle_school_next_url(next.get('href')),
                                 callback=self.parse_school)

    # 处理next url
    def handle_school_next_url(self, url):
        return url.replace('pcn=', 'pcn=高等学校')

    def parse_jingpin(self, response):
        soup = self.get_soup(response)
        titles = soup.select('div.threadlist_title > a')
        hrefs = list(map(lambda a: self.start_urls[0] + a.get('href')[1:], titles))
        for href in hrefs:
            yield scrapy.Request(url=href, callback=self.parse_page_info)
        next = soup.select_one('a.next')
        if next is not None:
            next_url = self.handle_school_next_url(next.get('href'))
            if next_url.find('tag') < 1:
                next_url.replace('ie=utf-8', 'ie=utf-8&tab=good')
            yield scrapy.Request(url='http:' + next_url, callback=self.parse_jingpin)

    def parse_page_info(self, response):
        soup = self.get_soup(response)
        # 正则匹配全文,获取邮箱和qq号
        text = soup.select_one('html').text.strip().replace('\n', '')
        #ba = soup.select_one('div.card_title > a').text.strip()
        datas = []
        emails = self.mail_pat.findall(text)
        qqs = self.qq_pat.findall(text)
        datas.extend(emails)
        datas.extend(qqs)
        # 存储到 数据库里
        for data in set(datas):
            item = BaidumailItem()
            # item['ba'] = ba
            item['data'] = data
            yield item
        # 寻找下一页
        titles = soup.select('li.pb_list_pager > a')
        if len(titles) < 1:
            return
        if titles[-2].text.strip() == '下一页':
            yield scrapy.Request(url=self.start_urls[0] + titles[-2].get('href'), callback=self.parse_page_info)

    def get_soup(self, response):
        html = response.text
        return BeautifulSoup(html, 'lxml')

