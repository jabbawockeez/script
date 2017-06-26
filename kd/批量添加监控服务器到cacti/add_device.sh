#!/bin/bash
###批量增加设备
IP_LIST=`cat /opt/script/cacti/list.txt`
for i in $IP_LIST
do
ID=`echo $i|awk -F \_ '{print $1}'`
IP=`echo $i|awk -F \_ '{print $2}'`
php /var/www/cacti/cli/add_device.php --description="$ID" --ip="$IP" --template=11  --avail=snmp --version=1 --community='public' --port=161 --timeout=500 --max_oids=10
done
echo '---------'
echo 'finished!'
