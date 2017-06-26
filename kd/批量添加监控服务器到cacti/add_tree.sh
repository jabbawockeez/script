### 批量添加节点到树
#!/bin/bash
#write 2013-05-08
#define orders
OD1="/usr/bin/php"
OD2="/var/www/cacti/cli"
host_id=$($OD1 $OD2/add_tree.php --list-hosts|grep IISTEST|awk '{print $1}')
for x in $host_id
do
$OD1 $OD2/add_tree.php --type=node --node-type=host --tree-id=14 --host-id=$x
done
echo ''
echo '----------'
echo 'finished!'
