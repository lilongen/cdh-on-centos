delete from mysql.user where mysql.user.user like 'cdh_%';

drop database if exists cmf;

drop database if exists cdh_hive;
drop database if exists cdh_activitymonitor;
drop database if exists cdh_reportsmanager;
drop database if exists cdh_oozie;
drop database if exists cdh_hue;
drop database if exists cdh_sentry;

create database cdh_hive default character set utf8;
create database cdh_activitymonitor default character set utf8;
create database cdh_reportsmanager default character set utf8;
create database cdh_oozie default character set utf8;
create database cdh_hue default character set utf8;
create database cdh_sentry default character set utf8;

grant all privileges on cdh_hive.* to cdh_hive@'%' identified by 'uydc.cmf' with grant option;
grant all privileges on cdh_activitymonitor.* to cdh_activitymonitor@'%' identified by 'uydc.cmf' with grant option;
grant all privileges on cdh_reportsmanager.* to cdh_reportsmanager@'%' identified by 'uydc.cmf' with grant option;
grant all privileges on cdh_oozie.* to cdh_oozie@'%' identified by 'uydc.cmf' with grant option;
grant all privileges on cdh_hue.* to cdh_hue@'%' identified by 'uydc.cmf' with grant option;
grant all privileges on cdh_sentry.* to cdh_sentry@'%' identified by 'uydc.cmf' with grant option;

flush privileges;
