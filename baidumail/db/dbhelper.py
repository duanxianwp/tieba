import pymysql
from baidumail import settings


class DBHelper(object):

    def __init__(self):
        self.db = pymysql.connect(settings.MYSQL_URL, settings.MYSQL_USERNAME, settings.MYSQL_PASSWORD,
                                  settings.MYSQL_DATABASE)

    def update_data(self, data):
        cursor = self.db.cursor()
        insert_sql = 'insert into {} (data) values({})'.format(settings.MYSQL_TABLE, data)
        try:
            cursor.execute(insert_sql)
            self.db.commit()
        except Exception:
            self.db.rollback()
