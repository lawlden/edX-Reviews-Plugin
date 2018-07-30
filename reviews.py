# -*- coding: utf-8 -*-
'''
--------------------------------------------------
            Reviews Backend Plugin v1.0
           Enstructo Incorporated, 2018
       Designed for use in conjunction with
         Feedback XBlock by Piotr Mitrios
     https://github.com/pmitros/FeedbackXBlock
----------->Open edX Ginkgo/Hawthorn<-------------
'''

from pandas import *
import os
import csv
import ast
import credentials
import utils
import sys

# establish SQL connection and populate DataFrame from review events
connection = utils.SQL()
report = connection.local_query("SELECT * FROM courseware_studentmodule WHERE module_type = 'feedback';", "edxapp")

out_path = "/ratings/dump"

# check for/remove duplicate reviews (based on most recently modified review)
report = report.sort_values(['course_id', 'student_id', 'modified'], ascending=True)
report = report.drop_duplicates(['course_id', 'student_id'], keep='last')

# remove superfluous sections
del report['done']
del report['grade']
del report['module_type']
del report['max_grade']
del report['created']
del report['id']
del report['module_id']

# establish lists
rating = []
response = []

# parse/populate Course ID & Date Objects
parse = utils.Parse()
report['course_id'] = parse.id(report)
report['modified'] = parse.date(report.modified, True)

# parse unicode dict & strip out ratings/responses
for i in report.state:
    d = ast.literal_eval(i)
    if 'user_vote' in d.keys():
        rating.append(d['user_vote']+1)
    else:
        rating.append("null")
    if 'user_freeform' in d.keys():
        review_text = d['user_freeform'].replace("\n","\\n")
        response.append(review_text)
    else:
        response.append("null")
report['rating'] = rating
report['response'] = response
del report['state']

# generate enrollment .csv file
if not os.path.exists(out_path):
    os.makedirs(out_path)
os.chdir(out_path)
fname = "reviews.csv"
report.to_csv(fname, sep="\t", index=False, header=False)

