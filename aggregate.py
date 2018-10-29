
import csv
import os
import re
import numpy
import pandas
import math
from datetime import datetime
from collections import OrderedDict

# establish variables/global dicts
out_path = "/ratings/dump"
filestore = "/ratings/dump/reviews.csv"
star_null = "<span class='fa fa-star-o' aria-hidden='true' style='color:rgb(210,210,210);'></span>"
star_empty = "<span class='fa fa-star-o' aria-hidden='true'></span>"
star_full = "<span class='fa fa-star' aria-hidden='true'></span>"
star_half_empty = "<span class='fa fa-star-half-empty' aria-hidden='true'></span>"
course_reviews = {}
counts = {}
courses = []
strings = []
averages = []
count = []
output = pandas.DataFrame()


# read reviews file & populate course-specific review lists
with open(filestore) as csv_file:
    readCSV = csv.reader(csv_file, delimiter='\t')
    try:
        c = 1
        for row in readCSV:
            course_number = row[0]
            rating = row[3]
            if not (row):
                continue
            elif course_number == "XDemoX":
                pass
            elif rating != "null":
                if course_number not in course_reviews.keys():
                    course_reviews[course_number] = [int(rating)]
                    counts[course_number] = 1
                else:
                    course_reviews[course_number].append(int(rating))
                    counts[course_number] += 1
            else:
                pass
    except:
       pass

# calculate aggregates
if course_reviews:
    for k, v in course_reviews.items():
        v = [value for value in v if value != 0]
        review_aggregate = numpy.mean(v)
        review_aggregate = round(review_aggregate * 2.0) / 2.0
        if str(review_aggregate).endswith('.0'):
             review_aggregate = int(review_aggregate)
        #output_dict[k]["aggregate"] = review_aggregate
        dec, whole = math.modf(review_aggregate)
        whole = int(whole)
        diff = int(5 - (whole+round(dec)))
        full_string = star_full*whole
        if dec:
            full_string = full_string+star_half_empty
            if whole <=4:
                diff = 4-whole
                full_string = full_string+(star_empty*diff)
        elif whole < 5:
            diff = 5-whole
            full_string = full_string+(star_empty*diff)
        #output_dict[k]["string"] = full_string
        courses.append(k)
        averages.append(review_aggregate)
        strings.append(full_string)
        count.append(counts[k])


output["course"] = courses
output["average"] = averages
output["string"] = strings
output["count"] = count

# generate aggregate .csv file
if not os.path.exists(out_path):
    os.makedirs(out_path)
os.chdir(out_path)
fname = "aggregates.csv"
output.to_csv(fname, sep="\t", index=False, header=False)
