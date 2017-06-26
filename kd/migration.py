from k3odbc20 import k3odbc
import kdtools
import re
from pprint import pprint
import xml.etree.ElementTree as ET



def has_lic1(new_MCIP, new_MCName, tenant_id):

    result = kdtools.execute_sql(new_MCIP, new_MCName, "select count(1) from t_bas_tenant where fid = '{}'".format(tenant_id))

    if int(result[0][0][0]) > 0:
        return True
    else:
        return False


def update_tenant_info_from_mc(new_MCIP, new_MCName, appip, databasename):
    kdtools.execute_sql('10.129.3.51', 'OMP', "update T_TenantInfoFromMC set MCName = '{}', MCIP = '{}', AppIP = '{}' where DatabaseName = '{}'".format(new_MCName, new_MCIP, appip, databasename))


def check_datacenterid(old_id, new_MCIP, new_MCName, databasename):
    try:
        new_id = kdtools.execute_sql(new_MCIP, new_MCName, "select FDATACENTERID from T_BAS_DATACENTER where FDATABASENAME = '{}'".format(databasename))[0][0][0]
    except:
        new_id = ''

    if new_id == old_id:
        return 'yes'
    else:
        return "id is not equal! new id: {}, old id: {}".format(new_id, old_id)


def update_mobile_settings(datacenter_id, old_MCIP, old_MCName, new_MCIP, new_MCName):
    result = kdtools.execute_sql(old_MCIP, old_MCName, "select FPARAMETERS from T_BAS_USERPARAMETER where FUSERID=-1 and FPARAMETEROBJID='AccId'")
    
    if len(result[0]) == 0:    # no settings
        return

    xml_str = result[0][0][0]

    # datacenter_id_list = re.sub('</?Root>', '', result[0][0][0]).split(',')
    # """
    # example:
    #     1. result[0][0][0] : <Root>20170330212212,20170425133717</Root>
    #     2. re.sub('</?Root>', '', result[0][0][0]) : 20170330212212,20170425133717
    #     3. re.sub('</?Root>', '', result[0][0][0]).split(',') : ['20170330212212', '20170425133717']
    # """

    tree = ET.fromstring(xml_str)

    # print tree.text
    datacenter_id_list = tree.text.split(',') if tree.text is not None else []  # if there is no data in the xml, the tree.text will be None

    if datacenter_id not in datacenter_id_list:   # the mobile settings doesn't enabled
        return


    # get the new MC's xml settings
    result = kdtools.execute_sql(new_MCIP, new_MCName, "select FPARAMETERS from T_BAS_USERPARAMETER where FUSERID=-1 and FPARAMETEROBJID='AccId'")

    try:
        if len(result[0]) == 0:     # the new MC has no settings before
            kdtools.execute_sql(new_MCIP, new_MCName, "insert into T_BAS_USERPARAMETER values(newid(), 'UserParameter', -1, 'AccId', CONVERT(xml, '<Root>{}</Root>'))".format(datacenter_id))
            # print "insert into T_BAS_USERPARAMETER values(newid(), 'UserParameter', -1, 'AccId', CONVERT(xml, '<Root>{}</Root>'))".format(datacenter_id)
        else:
            tree = ET.fromstring(result[0][0][0])
            
            if tree.text is None:   # the old xml settings is "<Root />"
                new_xml_str = '<Root>{}</Root>'.format(datacenter_id)  
            else:       # the old xml settings is like "<Root>xxx</Root>" or "<Root>xxx,yyy</Root>"
                new_xml_str = "<Root>{},{}</Root>".format(tree.text, datacenter_id)

            kdtools.execute_sql(new_MCIP, new_MCName, "Update T_BAS_USERPARAMETER set FPARAMETERS=CONVERT(xml, '{}') where FUSERID=-1 and FPARAMETEROBJID='AccId'".format(new_xml_str))
            # print "Update T_BAS_USERPARAMETER set FPARAMETERS=CONVERT(xml, '{}') where FUSERID=-1 and FPARAMETEROBJID='AccId'".format(new_xml_str)
    except Exception, e:
        return 'update mobile settings failed!' + str(e)




def get_MC_info(databasename, appip):

    get_old_MC_info_sql = "select MCName, MCIP, AppIP from T_TenantInfoFromMC where DatabaseName = '{}'".format(databasename)

    old_MC_info = kdtools.execute_sql('10.129.3.51', 'OMP', get_old_MC_info_sql)[0][0]

    # print old_MC_info

    config_file = '\\\\{}\d$\Program Files (x86)\Kingdee\K3Cloud\ManageSite\App_Data\Common.config'.format(appip)


    content = None
    with open(config_file, 'r') as f:
        content = f.read()

    new_MC_info = re.search('DatabaseEntity="(.*?)"\s.*\sDbServerInstance="(.*?)"', content, re.S).groups()

    return old_MC_info, new_MC_info


def func(args):

    appip = args['appip']
    databasename = args['databasename']


    # get old MC info
    # get_MC_info_sql = [
    #         "select MCName, MCIP, AppIP from T_TenantInfoFromMC where DatabaseName = '{}'".format(databasename), 
    #         # "select top 1 MCName, MCIP from T_TenantInfoFromMC where appip = '{}'".format(appip)
    #         ]

    
    try:
        old_MC_info, new_MC_info = get_MC_info(databasename, appip)

        old_MCName, old_MCIP, old_appip = old_MC_info
        new_MCName, new_MCIP = new_MC_info

        print old_MCName, old_MCIP, old_appip, new_MCName, new_MCIP
        
    except Exception, e:
        print 'get MC info error', e
        return kdtools.ErrMsg("error:get MC info.", e)
    # the format of the result of the execution would looks like: 
    # [ 
    #     [ (old_MCName, old_MCIP, old_appip), ], 
    #     [ (new_MCName, new_MCIP), ] 
    # ]



    get_AIS_info_sql = "select DisplayName, DomainName, DatabaseIP from T_TenantInfoFromMC where databasename = '{}'".format(databasename)
    try:
        DisplayName, DomainName, DatabaseIP = kdtools.execute_sql('10.129.3.51', 'OMP', get_AIS_info_sql)[0][0]
    except Exception, e:
        print 'get AIS info error', e
        return kdtools.ErrMsg("error:get AIS info.", e)
    

    # get tenant id
    get_tenant_id_sql = "select FTENANTID from T_BAS_DATACENTER where FDATABASENAME = '{}'".format(databasename)

    # get lic
    get_lic_sql = [
            # "select * from T_BAS_TENANT where FHOST = '{}'".format(DomainName), 
            "select * from T_BAS_TENANT where FID = '{}'",
            "select * from T_BAS_TENANT_L where FID = '{}'"
            ]

    print old_MCIP, old_MCName
    print new_MCIP, new_MCName

    tenant_id = ''

    try:
        tenant_id = kdtools.execute_sql(old_MCIP, old_MCName, get_tenant_id_sql)[0][0][0]
        print 'tenant id:{}'.format(tenant_id)

    except Exception, e:
        print 'get tenant id error', e
        return kdtools.ErrMsg("error:get tenant_id.", e)

    try:
        if tenant_id != '':
            lic_tenant = kdtools.execute_sql(old_MCIP, old_MCName, get_lic_sql[0].format(tenant_id))[0][0]
            lic_tenant_l = kdtools.execute_sql(old_MCIP, old_MCName, get_lic_sql[1].format(tenant_id))[0][0]

            # print lic_tenant
            # print lic_tenant_l
    except Exception, e:
        print 'get lic error', e
        return kdtools.ErrMsg("error:get lic.", e)


    # lic_tenant: ('57eb6fc571dc33','e8d216bcbff34be7b0bc0e62df637c86','A',0,None,'2016-11-04 20:18:24.573','2016-11-04 20:18:24.573','gg.test.ik3cloud.com')
    # lic_tenant_l: ('57eb6fc571dc34', '57eb6fc571dc33', 2052, 'xxxx company', ' ')

    # insert lic info to new MC
    insert_lic_sql = [
            "insert into T_BAS_TENANT values({})".format(','.join(["?"] * len(lic_tenant))),
            "insert into T_BAS_TENANT_L values({})".format(','.join(["?"] * len(lic_tenant_l)))
            ]

    # pprint(insert_lic_sql)


    con = None
    try:
        # if not has_lic(new_MCIP, new_MCName, DomainName):
            # kdtools.execute_sql(new_MCIP, new_MCName, *insert_lic_sql) format(*lic_tenant),
            # kdtools.execute_sql(new_MCIP, new_MCName, insert_lic_sql[0], lic_tenant)
        if not has_lic1(new_MCIP, new_MCName, tenant_id):
            con = k3odbc(new_MCIP, new_MCName)
            con.execute(insert_lic_sql[0], *lic_tenant)
            con.execute(insert_lic_sql[1], *lic_tenant_l)

            print 'insert lic success'
        else:
            print "found license on {}, skip to copy.".format(new_MCName)
    except Exception, e:
        print 'insert lic error', e
        return kdtools.ErrMsg("error:insert lic.", e)
    finally:
        if con is not None:
            con.close()

    datacenter_id = None

    # unreg
    try:
        datacenter_id = kdtools.unRegUser(old_MCIP, old_MCName, databasename)
        if datacenter_id == None:
            print 'unreg success'
            raise Exception("Get datacenterid failed!")
    except Exception, e:
        # print 'unreg error', e
        return kdtools.ErrMsg("error:unreg.", e)

    # reg
    try:
        kdtools.regUser(new_MCIP, new_MCName, databasename, DisplayName, DomainName.split('.')[0], DatabaseIP, datacenter_id)
        print 'reg success'
    except Exception, e:
        print 'reg error', e
        return kdtools.ErrMsg("error:reg.", e)

    # update tenant info from mc
    try:
        update_tenant_info_from_mc(new_MCIP, new_MCName, appip, databasename)

        print 'update tenant info from mc success'
    except Exception, e:
        print 'update tenant info from mc error', e
        return kdtools.ErrMsg("error:update tenant info from mc .", e)

    # check if the new datacenter id is equal to the old
    print 'checking datacenter id...', check_datacenterid(datacenter_id, new_MCIP, new_MCName, databasename)

    # update mobile settings
    if not ("TMP" in databasename or "TEST" in databasename):
        print "updating "
        update_mobile_settings(datacenter_id, old_MCIP, old_MCName, new_MCIP, new_MCName)

    return 'success: move {} from {} to {}'.format(databasename, old_appip, appip)
    # print 'success: move {} to {}'.format(databasename, appip)
    # print new_MCIP, new_MCName, databasename, DisplayName, DomainName.split('.')[0], DatabaseIP

