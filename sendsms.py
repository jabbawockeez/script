#!/usr/bin/env python
# coding: utf-8

import sys
import urllib
import urllib2


"""
##############
#  使用方法  #
##############

脚本接收参数输入：
    参数一：接收信息手机号列表，多个手机号之间用 逗号“,” 或 分号“;” 分隔，最多支持2000个
    参数二：短信内容列表，多条信息之间用 “空格” 分隔，最多支持1000条

    示例：
    python sendsms.py 13511111111,13522222222 "测试信息1" "测试信息2" "测试信息3"




######################
#  短信接口使用说明  #
######################

1、发送单条信息（get方式）

    url：http://...

    参数说明：
    user        用户名称
    pwd         用户密码 
    channel     系统为你分配的通道，不知道请填写空字符
    phonelist   手机号码，以英文分号（;）分割，最多一次100个号码
    cont        信息内容（注: 此字段内容必须采用UrlEncode转码,否则将出现错误或乱码.）
    extend      短信端口扩展字段，请按实际填写


2、发送多条信息（post方式）

    url：http://...

    以下是post主体：
    user=106test&pwd=106pwd&cont=<root>
    <sms><cont>testmsg1</cont><seq>123</seq><phonelist>13511111111;13522222222</phonelist><extend>01</extend></sms>
    <sms><cont>testmsg2</cont><seq>123</seq><phonelist>13511111111;13522222222</phonelist><extend>01</extend></sms>
    </root>

    参数说明：
    user            用户名称
    pwd             用户密码 
    cont            消息体内容，以xml字符串组成（注: 此字段内容中文出现的位置要以UrlEncode，gbk转码,否则将出现错误或乱码.）
    Xml中间的cont   当前sms节点短消息内容
    seq             当前内容和号码串的唯一id号，方便用户取匹配短信状态报告，seq由用户自己生成
    phonelist       当前内容的号码串，以英文分好（;）隔开，最大支持2000个号码
    extend          当前内容和号码串的扩展端口，请填写数字字符串
    sms             每条短信包的xml节点，每次提交允许有1000个sms节点，例如：<root><sms>…</sms><sms>…</sms><sms>…</sms>….<root>


"""

USER = "USERNAME"
PWD = "PASSWORD"
# CHANNEL = "CHANNEL"
# EXTEND = 110


def sendsms(phonelist, messagelist):
    """
    发送短信
    """

    if len(phonelist.split(',')) > 2000:
        raise Exception("Too many phone numbers!")

    if len(messagelist) > 1000:
        raise Exception("Too many messages!")

    cont_template = "<sms><cont>{message}</cont><seq>123</seq><phonelist>{phonelist}</phonelist><extend>01</extend></sms>"

    cont = '<root>'
    for message in messagelist:
        cont += cont_template.format(message = message, phonelist = phonelist)
    cont += "</root>"


    values = {
            'user' : USER,
            'pwd' : PWD,
            'cont' : cont,
            }
    
    data = urllib.urlencode(values)
    url = 'http://...'

    try:
        conn = urllib2.urlopen(url, data)
        # print conn.read()
    except Exception , e:
        print e
    else:
        print "success!"
        

if __name__ == '__main__':
    
    phonelist = sys.argv[1]
    messagelist = sys.argv[2:]
    
    sendsms(phonelist, messagelist)