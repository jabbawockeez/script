#!/usr/bin/python
# -*-coding: utf-8 -*-
#
# Author: jabba
# Create date: 2016-11-10
# Description: check backup file in s3 bucket 'ik3cloud'

from k3odbc20 import k3odbc

from boto.s3 import connect_to_region
from boto.s3.key import Key

from datetime import datetime, timedelta
import pdb


def send_mail_to_me(*args):
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header

    Error_DB_Name_And_IP_List , \
    Total, \
    Success_Count, \
    New_Tenant_Today = args

    Failed_Count = Total - Success_Count - len(New_Tenant_Today)
    
    sender = "YOUR_EMAIL"
    # 收件人，可以是多个
    receivers = ['123@qq.com', '456@qq.com']
    
    #print New_Tenant_Today
    #print [u', '.join(i) for i in New_Tenant_Today] 
    #print Error_DB_Name_And_IP_List
    #print map(lambda x: u', '.join(x), Error_DB_Name_And_IP_List)
    #print u'\n'.join(map(lambda x: u', '.join(x), Error_DB_Name_And_IP_List))

    msg = """
	Total: {}
	Success:{}
	New tenant(s): {}
{}
	Failed: {}
{}
    """.format(Total, \
    		Success_Count, \
    		len(New_Tenant_Today), \
    		'\n'.join(j for j in [u', '.join(i).encode('utf-8') for i in New_Tenant_Today]), \
    		Failed_Count, \
		'\n'.join(map(lambda x: u', '.join(x).encode('utf-8'), Error_DB_Name_And_IP_List))
		)

    print msg

#    msg = ''
#
#    msg += 'Total: {}\nSuccess: {}\n\n'.format(Total, Success_Count)
#
#    msg += 
#
#    for i in Error_DB_Name_And_IP_List:
#	KeyName, ip = i
#	msg += '{}, {}\n'.format(KeyName, ip.split('.')[0])

    
    # 三个参数：第一个为纯文本，第二个plain设置文本格式，第三个为编码格式
    message = MIMEText(msg,'plain','utf-8')
    message['From'] = Header('this is sender','utf-8')
    message['To'] = Header('this is receiver','utf-8')
    
    subject = 'upload success' if not Failed_Count else 'upload failed'
    message['Subject'] = Header(subject,'utf-8')
    
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.qq.com', 25)
        smtpObj.starttls()
        smtpObj.login(sender,'wbmekbkmqovsbeef')
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print 'send mail success!'
    except smtplib.SMTPException,e:
        print  e.message


def get_New_Tenant_Today():

	today = datetime.today().strftime("%Y-%m-%d")
	#today = "2017-05-01"
	
	try:
            con = k3odbc('10.129.3.51', 'OMP')
    
    	    con.execute("select DomainName, DisplayName from t_tenant where createdate > '{}'".format(today))

	    #return map(lambda x : x[0].split('.')[0], con.result)
	    return con.result
	    # the con.result would looks like this:
	    # [(DOMAIN1, TENANT1), (DOMAIN2, TENANT2), ...]
	except Exception, e:
	    print str(e)
	finally:
	    con.close()

	



def func():

    # get credentials
    with open('/home/ubuntu/.aws/credentials', 'r') as f:
        lines = f.readlines()

    credentials = {}
    for i in lines:
        if 'key' in i:
            k, v = [i.strip() for i in i.split('=')]
	    credentials[k] = v

    day = datetime.now().day
    month = datetime.now().month

    # BucketName = 'ik3cloud'
    Region = 'cn-north-1'

    JobTemplateName = '数据库日常备份3.0'

    getJobTemplateId = "select id from T_JobTemplete where name = '{}'".format(JobTemplateName)
    #getJobArgTemplateId_DBName = "select id from T_JobArgTemplete where JobTempleteId = '{JobTempleteId}' and Name = 'DBName'"
    #getJobArgTemplateId_S3Dir = "select id from T_JobArgTemplete where JobTempleteId = '{JobTempleteId}' and Name = 'S3Dir'"

    #getBackupTask_DBName = "select j.id, ja.value from T_Job j join T_JobArg ja on j.id = ja.jobid where j.JobTempleteid = '{JobTempleteId}' and j.IsValid = 1 and ja.JobArgTempleteId = {JobArgTempleteId_DBName} order by j.name"
    #getBackupTask_S3Dir = "select j.id, ja.value from T_Job j join T_JobArg ja on j.id = ja.jobid where j.JobTempleteid = '{JobTempleteId}' and j.IsValid = 1 and ja.JobArgTempleteId = {JobArgTempleteId_S3Dir} order by j.name"
    getBackupTask_DBName = "select j.id, ja.value from T_Job j join T_JobArg ja on j.id = ja.jobid where j.JobTempleteid = '{JobTempleteId}' and j.IsValid = 1 and ja.Name = 'DBName' order by j.id"
    getBackupTask_S3Dir = "select j.id, ja.value from T_Job j join T_JobArg ja on j.id = ja.jobid where j.JobTempleteid = '{JobTempleteId}' and j.IsValid = 1 and ja.Name = 'S3Dir' order by j.id"

    Log_File = '/tmp/upload_error_{month}_{day}.txt'.format(month = month, day = day)
    f = open(Log_File, 'w', buffering = 0)

    # get backup task from OMP
    OMP_Con = k3odbc('10.129.3.51', 'OMP')

    OMP_Con.execute(getJobTemplateId)
    JobTempleteId = OMP_Con.result[0][0]
    print JobTempleteId 
    #OMP_Con.execute(getJobArgTemplateId_DBName.format(JobTempleteId = JobTempleteId))
    #JobArgTempleteId_DBName = OMP_Con.result[0][0]
    #print JobArgTempleteId_DBName 
    #OMP_Con.execute(getJobArgTemplateId_S3Dir.format(JobTempleteId = JobTempleteId))
    #JobArgTempleteId_S3Dir = OMP_Con.result[0][0]

    #OMP_Con.execute(getBackupTask_DBName.format(JobTempleteId = JobTempleteId, JobArgTempleteId_DBName = JobArgTempleteId_DBName))
    OMP_Con.execute(getBackupTask_DBName.format(JobTempleteId = JobTempleteId))
    All_Task_DBName = OMP_Con.result
    #OMP_Con.execute(getBackupTask_S3Dir.format(JobTempleteId = JobTempleteId, JobArgTempleteId_S3Dir = JobArgTempleteId_S3Dir))
    OMP_Con.execute(getBackupTask_S3Dir.format(JobTempleteId = JobTempleteId))
    All_Task_S3Dir = OMP_Con.result

    Total = len(All_Task_DBName)
    #print 'Total:', Total
    f.write('Total: {}\n'.format(Total))

    Info_List = []
    i = 0
    while i < Total:
        if All_Task_DBName[i][0] == All_Task_S3Dir[i][0]:       # test if the jobid is equal
            #print All_Task_DBName[i][1], All_Task_S3Dir[i][1]

            BucketName = All_Task_S3Dir[i][1].split('/')[0]
            key = All_Task_S3Dir[i][1].split('/')[1] + '/' + All_Task_DBName[i][1] + '_{month}_{day}.zip'.format(month = month % 2, day = day)
            #print BucketName, key

            Info_List.append((BucketName, key))
            i += 1


    Success_Count = 0
    Error_List = []

    try:
        con = connect_to_region(Region, aws_access_key_id = credentials['aws_access_key_id'], aws_secret_access_key = credentials['aws_secret_access_key'])
    except Exception, e:
        f.write('{}'.format(','.join(e.args)))
	return


    New_Tenant_Today = get_New_Tenant_Today()
    #print '{} new tenant(s) today: '.format(len(New_Tenant_Today)), New_Tenant_Today 
    New_Domain = [i[0].encode('utf-8').split('.')[0] for i in New_Tenant_Today]
    print New_Domain 


    for i in Info_List:
        BucketName, KeyName = i

        bucket = con.get_bucket(BucketName)
        obj = bucket.get_key(KeyName)

        if obj is None:
	    if KeyName.split('/')[0] not in New_Domain:
	    	print KeyName
		Error_List.append(KeyName)
		print KeyName + ' not found'
		f.write('{} not found\n'.format(KeyName))
	    continue

        # test if the newest upload time is today
        last_modified_time = datetime.strptime(obj.last_modified, "%a, %d %b %Y %H:%M:%S GMT") + timedelta(hours = 8)   # convert to Chinese time

        now = datetime.now()
        if last_modified_time < (now - timedelta(hours = now.hour, minutes = now.minute)):	# older than today
            Error_List.append(KeyName)
            #print KeyName + ' ' +  obj.last_modified
            f.write('{} {}\n'.format(KeyName, obj.last_modified))
            continue

        Success_Count += 1

    #print Error_List
    #print 'Success:', Success_Count
    f.write('Success: {}\n'.format(Success_Count))

    getDetailInfoSql = "select databaseip from t_tenantinfofrommc where databasename = '{}' and databaseip not like '10.130%'"

    Error_DB_Name_And_IP_List = []

    for i in Error_List:
	DBName = '_'.join(i.split('/')[1].split('_')[0:4])
        OMP_Con.execute(getDetailInfoSql.format(DBName))

	f.write(DBName)	# write DBName
	#if len(OMP_Con.result[0]) > 0:
	if len(OMP_Con.result) > 0:	# if the sql statement returns no result, the result variable would be an empty list but not a list with an empty tuple, this is different from the pypyodbc module
	    f.write(' {}\n'.format(OMP_Con.result[0][0]))
	    Error_DB_Name_And_IP_List.append((i, OMP_Con.result[0][0])) 
	else:
	    f.write('\n')
	    Error_DB_Name_And_IP_List.append((i, '')) 

    OMP_Con.close()
    f.close()

    #if len(Error_List) > 0:
    send_mail_to_me(Error_DB_Name_And_IP_List , Total, Success_Count, New_Tenant_Today)

if __name__ == '__main__':
    func()

