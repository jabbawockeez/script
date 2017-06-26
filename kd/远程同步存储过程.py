from k3odbc20 import k3odbc
import kdtools

def func(args):

    # try:
    #     SureToCover = args['SureToCover'] or 0
    # except:
    #     SureToCover = 0

    SureToCover = args['SureToCover'] if args.ContainsKey('SureToCover') else 0

    target_ip_list = []

    if args['TargetIP'] == '*':
        try:
            get_all_db_ip = "select distinct databaseip from t_tenantinfofrommc order by databaseip"
            tmp = kdtools.execute_sql('10.129.3.51', 'OMP', get_all_db_ip)[0]
            target_ip_list = [i[0] for i in tmp]
        except Exception, e:
            return kdtools.ErrMsg('error: get all db ip failed!', e)

    else:
        target_ip_list = args['TargetIP'].split(';')

    get_SPDef_sql = """SELECT definition FROM sys.sql_modules WHERE object_id = (OBJECT_ID(N'{}'))""".format(args['SPName'])
    drop_SP_sql = """DROP PROCEDURE {}""".format(args['SPName'])

    try:
        source_con = k3odbc(args['SourceIP'], 'master', 'USER', 'PASSWORD')
        source_con.execute(get_SPDef_sql)

        SP_def = source_con.result[0][0]
    except Exception, e:
        return 'get sp definition failed: ' + ', '.join(e.args)

    target_con = None

    for target_ip in target_ip_list:

        try:
            target_con = k3odbc(target_ip, 'master', 'dbuser', 'PASSWORD')

            target_con.execute(get_SPDef_sql)

            if len(target_con.result) > 0:    # target_con.result is not None
                if SureToCover:
                    target_con.execute(drop_SP_sql)

            target_con.execute(SP_def)

        except Exception, e:
            return 'create sp failed: ' + target_ip + ' ' + ', '.join(e.args)

        finally:
            target_con.close()

    return 'copy {} success: '.format(args['SPName']) + ', '.join(target_ip_list)
