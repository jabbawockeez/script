#!/bin/bash
# 
# Author: jabba
# Create date: 2016-12-28
# Description: get total size of all buckets except 'dining' in s3


sum=0

for i in `sudo aws s3 ls | awk '{print $3}' | grep -v dining`
do
	size=`sudo aws s3api list-objects --bucket $i --output json --query 'sum(Contents[].Size)'`
	sum=`expr $sum + $size`
done

echo `expr $sum / 1024 / 1024 / 1024` "GB"
