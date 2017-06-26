#!/usr/bin/python
#
# Author: jabba
# Create Date: 2017-06-13
# Description: display all tasks' name for the given queue name


import os
import sys
import subprocess
import pprint
import kdtools
import json
import base64
import time


QUEUE_NAME_PREFIX = 'PREFIX_STRING'


def queue_exists(queue_name):
	try:
		subprocess.check_output("sudo rabbitmqctl list_queues | grep -E '{}\s'".format(queue_name), shell = True)
		return True
	except Exception, e:
		#print e
		return False


def get_job_info_list(queue_name):

	job_info_list = []

	# get message count
	message_count = int(subprocess.check_output("sudo rabbitmqctl list_queues | grep -E '{}\s' | awk '{{print $NF}}'".format(queue_name), shell = True))
	#print 'message count {}'.format(message_count)

	if message_count == 0:
		return job_info_list

	all_messages = subprocess.check_output("sudo rabbitmqadmin get queue='{}' count='{}' | sed -e '1,3d' -e '$d'".format(queue_name, message_count), shell = True).split('\n')

	# The format of one message in a queue in rabbitmq is shown below, and we should get the value of the payload field.
	# | routing_key | exchange | message_count | payload | payload_bytes | payload_encoding | properties | redelivered |

	all_payloads = [i.split('|',4)[-1].rsplit('|', 5)[0].strip() for i in all_messages if i != '']  # the last object in all_message is ''


	#print all_payloads

	all_payloads.reverse()

	for i in all_payloads:


		try:
			#print i, type(i)
			j = json.loads(i.replace('\r\n', ''), encoding = 'gb2312')
		except Exception, e:
			j = json.loads(base64.decodestring(i).replace('\r\n', ''), encoding = 'gb2312')		

		#print j
		
		job_id = j['id']
		job_args = j.get('args', ['no args'])
		#print j['messageType']


		if j['messageType'] == 0:	# message from OMP
			jobtemplatename, name = kdtools.execute_sql('10.129.3.51', 'OMP', "select jobtempletename, name from t_job where id = '{}'".format(job_id))[0][0]
		elif j['messageType'] == 1:	# message from ik3cloud
			try:
				jobtemplatename = 'ik3cloud:' + kdtools.execute_sql('10.129.3.51', 'OMP', \
					"select commandName from T_CommandHistory where id = (select commandHistoryId from T_CommandHistoryDetail where id = '{}')".format(job_id))[0][0][0]
			except:
				jobtemplatename = 'unknown message from ik3cloud'

			name = ''
		else:
			jobtemplatename = 'unknown message'
			name = ''

		job_info_list.append([jobtemplatename, name, job_args])

	return job_info_list





def display_job_info(queue_name, job_info_list):

	print 'messages of {}\n'.format(queue_name)

	if len(job_info_list) == 0:
		print "no message in the queue '{}'".format(queue_name)
	else:
		for index, one_job in enumerate(job_info_list):
			print "{:<4}{} {} {}".format(index + 1, one_job[0].encode('utf-8'), one_job[1].encode('utf-8'), one_job[2])
			#print "{:<4}{}  {}".format(index + 1, one_job[0].encode('utf-8'), one_job[2])

	print '\n'




def get_queue_name():

	queue_list = subprocess.check_output("sudo rabbitmqctl list_queues | grep -Ev 'ik3cloud|\s0$'", shell = True).split('\n')[1:-2]

	# The queue_list would looks like(Note that both the COUNT1 and COUNT2 are bigger than 0):
	# QUEUE_NAME1	COUNT1
	# QUEUE_NAME2	COUNT2
	# ...

	for index, queue in enumerate(queue_list):
		print "{:<3}{}".format(index, queue)

	selection = raw_input("\nselect a queue to watch('q' to quit, 'r' to refresh): ")

	if selection == 'q':
		exit(0)
	elif selection == 'r':
		return None
	elif selection.isdigit() and int(selection) < len(queue_list):
		return queue_list[int(selection)].split()[0]
	else:
		print "Invalid input!\n\n"
		return None



def get_into_loop():
	while True:
		queue_name = None

		os.system('clear')
		queue_name = get_queue_name()
		#print queue_name

		if queue_name is None:
			continue

		os.system('clear')

		job_info_list = get_job_info_list(queue_name)

		display_job_info(queue_name, job_info_list)

		raw_input("\n\npress enter to continue...")

def show_usage():

	#print "Please specify the ip address of the queue name!\nExample: If a queue named 'kingdee.queue.shells.10.130.1.1', you must give the ip 10.130.1.1 as the argument."

	print """
This script can only be used to watch the queues which names are ended up with server ip.

If you want to watch a specified queue, just give the ip address, while the prefix of the queue name is hardcoded.
Example: If a queue named '{}.10.130.1.1', you must give the ip 10.130.1.1 as the argument, like "python watchmq.py 10.130.1.1"

If no argument specified, then you will get into the watch loop.
Note that the loop mode would NOT auto refresh, so you should press 'r' followed by enter to achive this. 
Just follow the instructions in the mode to get further operations.
""".format(QUEUE_NAME_PREFIX)



def main():

	if len(sys.argv) < 2:	# if no argument specified, then get into the watch loop
		get_into_loop()

	elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
		show_usage()

	else:

		queue_name = QUEUE_NAME_PREFIX + sys.argv[1]

		if not queue_exists(queue_name):
			print "queue name '{}' does not exists!".format(queue_name)
			exit(2)

		job_info_list = get_job_info_list(queue_name)

		display_job_info(queue_name, job_info_list)


if __name__ == "__main__":
	main()
