#!/usr/bin/python
# Author: jabba
# Create date: 2016-12-29
# Description: Count total upload size between two dates.
#              If both of the "START_TIME" and "END_TIME" are not given, then the script would count the size uploaded today. 

from boto.s3 import *
from datetime import datetime, timedelta
import sys
import argparse


def get_args():

    def mkdate(dateString):
        return datetime.strptime(dateString, '%Y-%m-%d')

    parser = argparse.ArgumentParser(description = "get total upload size in s3")

    parser.add_argument('--human-readable', action = 'store_true', help = 'print sizes in human readable format')

    # add start date argument
    parser.add_argument('-s', '--start-date',
        dest = 'start_date',
        type = mkdate,
        help = 'format: yyyy-mm-dd',
        default = datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0))

    # add end date argument
    parser.add_argument('-e', '--end-date',
        dest = 'end_date',
        type = mkdate,
        help = 'format: yyyy-mm-dd',
        default = datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0) + timedelta(days = 1))

    args = parser.parse_args()

    #print 'start date: {}\nend date: {}\n'.format(args.start_date, args.end_date)

    if args.start_date > args.end_date:
        raise Exception('Invalid date!')

    return args


# get credentials
def get_credentials():
    credentials = {}

    with open('/home/ubuntu/.aws/credentials', 'r') as f:
        lines = f.readlines()

    for i in lines:
        if 'key' in i:
            k, _, v = i.split()
            credentials[k] = v

    return credentials


def main():
    args = get_args()
    credentials = get_credentials()


    region = 'cn-north-1'

    # connect to region
    con = connect_to_region(region, **credentials)

    all_buckets = con.get_all_buckets()

    bucket_size_dict = {}
    # bucket_size_dict would looks like below:
    # {
    #     'bucket1' : [upload_size, bucket_total_size],
    #     'bucket2' : [upload_size, bucket_total_size]
    #      ...
    # }

    for bucket in all_buckets:
        upload_size = 0
        bucket_total_size = 0

        # ignore the bucket 'dining'
        if bucket.name == 'dining':
            continue


        for key in bucket:

            bucket_total_size += key.size

            last_modified_date = datetime.strptime(key.last_modified, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours = 8)

            if last_modified_date >= args.start_date and last_modified_date < args.end_date:
		#print key.name, last_modified_date, args.start_date, args.end_date
                upload_size = upload_size + key.size
                #print key.name, key.last_modified

        bucket_size_dict[bucket.name] = [upload_size, bucket_total_size]


    s3_total_size = 0
    for k, v in bucket_size_dict.items():
        s3_total_size += v[1]

        if args.human_readable:
	    print "{} {} GB".format(k, v[0] * 1.0 / 1073741824)
	else:
	    print "{:<20} {:<25} GB".format(k, v[0] * 1.0 / 1073741824)

    print '{:<20} {:<25} GB'.format('total', s3_total_size * 1.0 / 1073741824)



if __name__ == '__main__':
    main()
