insert into thold_data(
	name,
	rra_id,
	data_id,
	graph_id,
	graph_template,
	data_template,
	thold_hi,
	thold_low,
	thold_fail_trigger,
	thold_fail_count,
	time_hi,
	time_low,
	time_fail_trigger,
	time_fail_length,
	thold_warning_hi,
	thold_warning_low,
	thold_warning_fail_trigger,
	thold_warning_fail_count,
	time_warning_hi,
	time_warning_low,
	time_warning_fail_trigger,
	time_warning_fail_length,
	thold_alert,
	thold_enabled,
	thold_type,
	bl_ref_time_range,
	bl_pct_down,
	bl_pct_up,
	bl_fail_trigger,
	bl_fail_count,
	bl_alert,
	lastread,
	lasttime,
	oldvalue,
	repeat_alert,
	notify_default,
	notify_extra,
	notify_warning_extra,
	notify_warning,
	notify_alert,
	host_id,
	syslog_priority,
	data_type,
	cdef,
	percent_ds,
	expression,
	template,
	template_enabled,
	tcheck,
	exempt,
	restored_alert,
	bl_thold_valid
)
select distinct concat(a.name_cache, ' [hdd_used]') name,
	a.local_data_id rra_id,
	d.id data_id,
	b.local_graph_id graph_id,
	b.graph_template_id graph_template,
	a.data_template_id data_template,
	85 thold_hi,
	0 thold_low,
	1 thold_fail_trigger,
	0 thold_fail_count,
	null time_hi,
	null time_low,
	1 time_fail_trigger,
	1 time_fail_length,
	70 thold_warning_hi,
	0 thold_warning_low,
	6 thold_warning_fail_trigger,
	0 hold_warning_fail_count,
	null time_warning_hi,
	null time_warning_low,
	1 time_warning_fail_trigger,
	1 time_warning_fail_length,
	0 thold_alert,
	'on' thold_enabled,
	0 thold_type,
	86400 bl_ref_time_range,
	20 bl_pct_down,
	20 bl_pct_up,
	2 bl_fail_trigger,
	0 bl_fail_count,
	0 bl_alert,
	null lastread,
	'0000-00-00 00:00:00' lasttime,
	null oldvalue,
	6 repeat_alert,
	null notify_default,
	'glc@kingdee.com;ziquan_liu@kingdee.com;jack_zeng@kingdee.com;rest_chen@kingdee.com' notify_extra,
	'glc@kingdee.com;ziquan_liu@kingdee.com;jack_zeng@kingdee.com;rest_chen@kingdee.com' notify_warning_extra,
	0 notify_warning,
	0 notify_alert,
	c.id host_id,
	3 syslog_priority,
	1 data_type,
	27 cdef,
	'hdd_used' percent_ds,
	'\N' expression,
	2 template,
	'on' template_enabled,
	0 tcheck,
	'off' exempt,
	'off' restored_alert,
	0 bl_thold_valid
from data_template_data a, graph_templates_graph b, host c, data_template_rrd d
where a.name_cache=b.title_cache
and a.name_cache like '%Used Space%Label%'
and left(a.name_cache, locate(' - Used Space', a.name_cache)-1)=c.description
and d.local_data_id=a.local_data_id
and d.data_source_name='hdd_used'
and not exists
(select 1 from thold_data t where t.name like concat(a.name_cache,'%'))
