#-*- coding: utf-8 -*-

#import pypyodbc
import pymssql

# k3odbc 2.0
# 执行统一使用execute方法，结果保存在result属性中

class k3odbc:


    def __init__(self, server, database = 'master', user = 'USER', password = 'PASSWORD'):
        self.server = server
        self.database = database
        self.user = user
        self.password = password

        self.con = self.connect()
        self.cursor = self.con.cursor()
        self.result = None

    def connect(self):

        #connectString = "DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % (
        #        self.server, self.database, self.user, self.password)
        connectString = "host = %s, database = %s, user = %s, password = %s, " % (
                self.server, self.database, self.user, self.password)
        con = None

        try:
            #con = pypyodbc.connect(connectString, autocommit = True, timeout = 1200)
            con = pymssql.connect(host = self.server, database = self.database, 
		user = self.user, password = self.password, autocommit = True, timeout = 1200)
        except Exception, e:
            raise e
	
	return con

    def execute(self, sql, args = None):

        try:
            self.cursor.execute(sql, args)
            self.result = self.cursor.fetchall()
        #except pypyodbc.ProgrammingError, e:
        #    """A ProgrammingError exception is raised if no SQL has been executed or if it did not return a result set (e.g. was not a SELECT statement)."""
        except Exception, e:
            self.result = None
            raise e
        
        while self.cursor.nextset():
            pass

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.con:
            self.con.close()


# example
# try:
#     con = k3odbc('localhost', 'master', 'sa', 'PWD')
#     con.execute('SELECT * FROM table')
# except Exception, e:
#     print e
# finally:
#     print con.result
#     con.close()
