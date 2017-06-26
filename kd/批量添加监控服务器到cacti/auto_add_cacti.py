#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# Author: jabba
# Create date: 2017-06-02
# Description: 
#	Auto add app server to cacti.
#	Using shell scripts in the directory stored in configurable variable SCRIPT_PATH below.



import MySQLdb as mdb
import subprocess


SCRIPT_PATH  = '/opt/script/cacti/batchaddcacti170512/'
host = 'localhost'


def update_server_list_file(cursor = None):
	if not cursor:
		return False

	# get new server info
	sql = """
		select distinct concat(case when a.tenanttype=1 then 'K3Cloud-M-' else 'K3Cloud-S-' end, a.hostaddress, '_', a.hostaddress)
		from t_sys_tenant a
		where tenantstatus='正常'
		and hostaddress not like '10.130.6.7910.130.6.79:443;'
		and not exists(
			select 1 from cacti.host b
				where a.hostaddress=b.hostname
			)
		order by 1
	"""

	result = None

	try:
		cursor.execute('use BI')
		cursor.execute(sql)
		result = cursor.fetchall()
		# the result would look like this:
		# ((u'K3Cloud-M-10.130.7.173_10.130.7.173',), (u'K3Cloud-M-10.130.7.175_10.130.7.175',), (u'K3Cloud-S-10.130.7.210_10.130.7.210',))
	except:
		#print str(e)
		return False


	print 'found new servers:\n{}'.format('\n'.join([i[0] for i in result]))


	if result:

		multilist = SCRIPT_PATH + 'multilist.txt'
		singlelist = SCRIPT_PATH + 'singlelist.txt'

		try:

			with open(multilist, 'w') as m_f, open(singlelist, 'w') as s_f:

				for i in result:
					if '-S-' in i[0]:
						s_f.write(i[0] + '\n')
					else:
						m_f.write(i[0] + '\n')

		except:
			#print str(e)
			return False
		else:
			return True

	else:
		return False


def add_to_cacti():

	try:
		subprocess.check_call(['sh', SCRIPT_PATH + 'cacti_multi.sh'], cwd = SCRIPT_PATH)
		subprocess.check_call(['sh', SCRIPT_PATH + 'cacti_single.sh'], cwd = SCRIPT_PATH)
	except:
		print 'failed! Add to cacti'
	
			
def exec_sql_file(cursor = None):

	if not cursor:
		return False

	#sql_files = ['data_amend.sql', 'add_cpu.sql']
	sql_files = ['data_amend.sql', 'add_cpu.sql', 'add_disk.sql', 'add_mem.sql']


	cursor.execute('use cacti')

	for i in sql_files:
		with open(i, 'r') as f:
			try:
				cursor.execute(f.read())
				while cursor.nextset():
					pass
				print 'success: {}'.format(i)
			except Exception, e:
				print 'failed! {}'.format(i), e
				continue
			
	

def main():

	# connect to db
	conn = mdb.connect(host = host, charset = 'utf8')
	conn.autocommit(1)
	cur = conn.cursor()

	#update_server_list_file(cur)
	#exec_sql_file(cur)
	if update_server_list_file(cur):
		add_to_cacti() 
		exec_sql_file(cur)
		

	if cur:
		cur.close()
	if conn:
		conn.close()

	

if __name__ == '__main__':
	main()
