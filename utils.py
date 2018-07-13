import pymysql.cursors
import MySQLdb
import credentials
import sys
import re
import csv
import subprocess
import os
import smtplib
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt

# define global datetime variables
today = dt.today()
period_dt = (dt.today() + relativedelta(months=-1))
month = period_dt.strftime('%B')
year = period_dt.strftime('%Y')
timestamp = today.strftime('%Y/%m/%d %H:%M:%S')


class SQL:
    # query local database and return tuple of results
    def local_query(self, query, database):
        check = Check()
        report = pd.DataFrame()
        try:
            connection = pymysql.connect(host='localhost',
                                         user='root',
                                         db=database,
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
        except:
            check.status("fail")
            sys.exit()

        try:
            with connection.cursor() as cursor:
                sql = query
                cursor.execute(sql)
                dump = cursor.fetchall()
                if dump:
                    report = pd.DataFrame.from_dict(dump)
                else:
                    check.status("empty")
                    sys.exit()
        finally:
            connection.close()
        return report

class Parse:
    # parse course id string & populate course_id_list
    def id(self, dataframe):
        course_id_list = []
        for course_id_string in dataframe.course_id:
            replace = course_id_string.replace("+", "X")
            id_number = re.search('X(.*)X', replace).group(1)
            course_id_list.append(id_number)
        return course_id_list


    # format datetime objects
    def date(self, column, hour):
        dates = []
        for d in column:
            if hour == True:
                n = d.strftime('%m/%d/%Y %H:%M')
            else:
                n = n = d.strftime('%m/%d/%Y')
            dates.append(n)
        return dates


class Check():
    # establish status checking
    def status(self, active):
        status_path = '/ratings/log/'
        try:
            os.stat(status_path)
        except:
            os.mkdir(status_path)
        check = status_path+"STATUS.CHECK"
        fail = status_path+"STATUS.FAIL"
        empty = status_path+"STATUS.EMPTY"
        statuses = {"check":check, "fail":fail, "empty":empty}
        for key, value in statuses.items():
            if key == active:
                if not os.path.exists(value):
                    open(value, 'w').close()
            else:
                if os.path.exists(value):
                    os.remove(value)


    # write to stderr & stdout logs
    def log(self, logfile, script, message):
        with open('/ratings/log/{}'.format(logfile), 'a') as f:
            f.write("{}: {} -- {}\n".format(script, timestamp, message))
