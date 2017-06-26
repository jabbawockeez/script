# coding: utf-8

import os
import subprocess
from k3odbc20 import k3odbc


# backup database
def backup(ServerIP, DatabaseName, BakFilePath):
    '''
    backup DatabaseName to BakFilePath on ServerIP
    '''

    try:
        con = None

        if not dbExists(ServerIP, DatabaseName):
            raise Exception("{} not found on {}".format(DatabaseName, ServerIP))
        else:
            con = k3odbc(ServerIP)
            con.execute("""BACKUP DATABASE {0} TO DISK = '{1}' WITH COMPRESSION, INIT""".format(DatabaseName, BakFilePath))
    except Exception, e:
        # raise KdException('kdtools.backup', e)
        print 'test'
    finally:
        if con:
            con.close()


# restore database
def restore(ServerIP, DatabaseName, BakFilePath):
    '''
    restore DatabaseName using BakFilePath on ServerIP
    '''

    # check if the bak file exists
    if not os.path.exists(BakFilePath):
        raise Exception('backup file {} not found'.format(BakFilePath))

    con = None

    try:
        con = k3odbc(ServerIP)
        con.execute("""exec p_RestoreK3DB '{}', '{}' """.format(DatabaseName, BakFilePath))
    except Exception, e:
        raise KdException('kdtools.restore', e)
    finally:
        if con:
            con.close()


# execute sql command(s) directly
def execute_sql(ServerIP, DatabaseName, *sql):

    result_set = []
    con = None

    try:
        con = k3odbc(ServerIP, DatabaseName)

        for i in sql:
            con.execute(i)

            if con.result is not None:
                result_set.append(con.result)

    except Exception, e:
        raise KdException('kdtools.execute_sql', e)
    finally:
        if con:
            con.close()

    return result_set

# regUser
def regUser(MCIP, MCName, DatabaseName, DisplayName, HostPrefix, DatabaseIP, DatacenterID = ''):

    con = None

    try:
        con = k3odbc(MCIP)
        RegSql ="exec p_RegUser20 '{}', '{}', '{}', '{}', '{}', '{}'".format(MCName, DatabaseName, DisplayName, HostPrefix, DatabaseIP, DatacenterID)
        con.execute(RegSql)
        
    except Exception, e:
        return KdException('kdtools.regUser', e)
    finally:
        if con:
            con.close()


# regUser multi
def regUser_multi():
    pass

# regUser single
def regUser_single():
    pass

# regUser test
def regUser_test():
    pass

# unRegUser
def unRegUser(MCIP, MCName, DatabaseName):

    con = None
    datacenter_id = None

    try:
        con = k3odbc(MCIP)
        con.execute("select FDATACENTERID from {}..t_bas_datacenter".format(MCName))
        datacenter_id = con.result[0][0]

        con.execute("""exec p_UnRegUser '{}', '{}' """.format(MCName, DatabaseName))
    except Exception, e:
        raise KdException('kdtools.unRegUser', e)
    finally:
        if con:
            con.close()

    return datacenter_id


# change name


# compress
def compress(ZipFilePath, BakFilePath):
    try:
        # subprocess.Popen(r"""C:\Program Files\7-Zip\7z.exe a -tzip -mx1 -mmt {} {}""".format(ZipFilePath, BakFilePath))
        subprocess.check_call(r"""C:\Program Files\7-Zip\7z.exe a -tzip -mx1 -mmt {} {}""".format(ZipFilePath, BakFilePath))
    except Exception, e:
        raise KdException('kdtools.compress', e)


# upload
def upload(S3Dir, ZipFilePath):
    try:
        subprocess.check_call(r"""C:\CloudHousing\AWS.S3.Uploader.exe {} {} application/zip""".format(S3Dir, ZipFilePath))
    except Exception, e:
        raise KdException('kdtools.upload', e)


# build error message as a string
def ErrMsg(msg = '', ExceptionObj = None):
    if ExceptionObj is not None:
        m = msg + ' ' + ', '.join(ExceptionObj.args)
    else:
        m = msg

    return m


# check if database exists
def dbExists(ServerIP, DatabaseName):

    con = None
    
    try:
        con = k3odbc(ServerIP)

        con.execute("""SELECT 1 FROM 
            sys.databases WHERE name = '{}'""".format(DatabaseName))

        if len(con.result) > 0:
            return True
        else:
            return False
    except Exception, e:
        raise KdException('kdtools.dbExists', e)
    finally:
        if con:
            con.close()

# 计算python程序执行时间

# 方法1
# import datetime
# starttime = datetime.datetime.now()
# #long running
# endtime = datetime.datetime.now()
# print (endtime - starttime).seconds

# 方法 2
# start = time.time()
# run_fun()
# end = time.time()
# print end-start

# 方法3
# start = time.clock()
# run_fun()
# end = time.clock()
# print end-start

# 方法1和方法2都包含了其他程序使用CPU的时间，是程序开始到程序结束的运行时间。
# 方法3算只计算了程序运行的CPU时间


# self defined exception
class KdException(Exception):

    def __init__(self, msg = 'default KdException message', e = Exception('default KdException')):
        super(KdException, self).__init__()

        l = list(e.args)
        l.insert(0, msg)
        self.args = tuple(l)