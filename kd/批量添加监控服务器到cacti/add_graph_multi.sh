#!/bin/bash
###增加图形add_graph.sh
P1=/usr/bin/php
P2=/var/www/cacti/cli/
P3=/var/www/cacti/cli/add_graphs.php
ID=$($P1 $P2/add_tree.php --list-hosts|grep K3Cloud-M|awk '{print $1}')
for i in $ID
do
##add graphs type2
#Process
$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=29

#TCP Connection
$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=35

#IIS
$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=55
$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=56
$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=57
$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=58

#CPU
#Host MIB - Multi CPU Utilization on 2 Processor Box
$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=51
####Host MIB - Multi CPU Utilization on 4 Processor Box
###$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=52
####Host MIB - Multi CPU Utilization on 8 Processor Box
###$P1 $P3 --host-id=$i --graph-type=cg --graph-template-id=53
#CPU0
$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=51 --snmp-query-id=9 --snmp-query-type-id=19 --snmp-field=hrProcessorFrwID --snmp-value=0
#CPU1
$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=51 --snmp-query-id=9 --snmp-query-type-id=19 --snmp-field=hrProcessorFrwID --snmp-value=1

#Disk
$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=26 --snmp-query-id=8 --snmp-query-type-id=18 --snmp-field=hrStorageIndex --snmp-value=1
$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=26 --snmp-query-id=8 --snmp-query-type-id=18 --snmp-field=hrStorageIndex --snmp-value=2
$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=26 --snmp-query-id=8 --snmp-query-type-id=18 --snmp-field=hrStorageIndex --snmp-value=3
$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=26 --snmp-query-id=8 --snmp-query-type-id=18 --snmp-field=hrStorageIndex --snmp-value=4

#Interface
###$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=33 --snmp-query-id=1 --snmp-query-type-id=22 --snmp-field=ifIP --snmp-value="10.130.6.62"
$P1 $P3 --host-id=$i --graph-type=ds --graph-template-id=33 --snmp-query-id=1 --snmp-query-type-id=22 --snmp-field=ifDescr --snmp-value="AWS PV Network Device #0"

done

