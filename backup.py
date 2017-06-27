#!/usr/bin/python
#_*_ coding : utf8 _*_
# Backup all databases in MySQL.

import os,time

USERNAME = 'root'
PASSWORD = 'root'
BACKUP_DIR = '/backup/'
NOWDATE = time.strftime('%Y-%m-%d')

def backup(DB_LIST):
	# test the directory to store backup files.
	if not os.path.exists(BACKUP_DIR):
		os.mkdir(BACKUP_DIR)

	for DB in DB_LIST:
		if not os.path.exists(BACKUP_DIR + DB):
			os.mkdir(BACKUP_DIR + DB)
		CMD = "mysqldump -u%s -p%s -B %s | gzip > %s/%s_%s.sql.gz" % (USERNAME, PASSWORD, DB, BACKUP_DIR + DB, DB, NOWDATE)
		os.popen(CMD)

def get_databases():
	CMD = "mysql -u%s -p%s -e 'show databases;' | sed '1d'" % (USERNAME, PASSWORD)
	# return a list of databases to be backuped.
	return os.popen(CMD).read().split()

if __name__ == '__main__':
	backup(get_databases())
