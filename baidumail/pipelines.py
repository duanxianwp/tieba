# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from baidumail.db.dbhelper import DBHelper


class BaidumailPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):

    def open_spider(self, spider):
        self.client = DBHelper()

    def close_spider(self, spider):
        self.client.db.close()

    def process_item(self, item, spider):
        self.client.update_data(item['data'])
        return item
