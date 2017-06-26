#!/bin/bash
# 
# Author: jabba
# Description: get all tasks' id for the given queue name(stored in QUEUE_NAME) from the rabbitmq



CONTENT=''
LENGTH=0

QUEUE_NAME=$1

get_queue_length()
{
	LENGTH=$(sudo rabbitmqctl list_queues | grep "$1" | awk '{print $NF}')
}

get_queue_content()
{
	CONTENT=$(sudo rabbitmqadmin get queue="$1" count="$2" | sed '1d' | awk -F'|' '{print $5}' | tr -d ' ' | grep -v '^$' | sed '1d')
}

if [ x"$1" == x ]; then 
	echo "please specify the queue name"
	exit 1
else
	get_queue_length $QUEUE_NAME
	get_queue_content $QUEUE_NAME $LENGTH
fi


for i in `echo $CONTENT`
do
	#echo $i
	job_id=$(echo $i | base64 -d - | jq '.id' | tr -d '"')
	echo $job_id
done
