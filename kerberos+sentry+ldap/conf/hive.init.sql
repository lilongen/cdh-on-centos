-- https://www.cloudera.com/documentation/enterprise/5-15-x/topics/sg_hive_sql.html



# CDH6.3 issue:
# beeline connect: principal should use primary/exact_instance@REALM,
# example hive/uydc-101@UYDC.COM, not hive/_HOST@UYDC.COM
!connect jdbc:hive2://10.200.70.161:10000/;principal=hive/ydc-161@UYDC.COM
!connect jdbc:hive2://10.200.70.161:10000/;principal=hive/_HOST@UYDC.COM
show databases;

create role r_admin;
grant all on server server1 to role r_admin;
grant all on server server1 to role r_admin with grant option;
grant role r_admin to group hive;
create role r_dev;
create role r_etl;
create role r_prod;
create role r_test;
show roles;

grant role r_prod to group g_prod;
grant role r_etl to group g_etl;
grant role r_dev to group g_dev;

create database yxt;
create database yxt_dirty;
create database yxt_gz;
create database yxt_orc;
create database yxt_parquet;

grant all on database yxt to role r_etl;
grant all on database yxt_dirty to role r_etl;
grant all on database yxt_gz to role r_etl;
grant all on database yxt_orc to role r_etl;
grant all on database yxt_parquet to role r_etl;
-- GRANT <Privilege> ON URIs (HDFS and S3A)
grant all on uri 'hdfs://ydc-162:8020/ws.kylin' to role r_kylin;

use default;
create table t1 (f1 int);
create table t2 (f1 int);
insert into t1 values (1), (2), (3), (4), (5);
insert into t2 values (1), (2), (3), (4), (5);

create database test_db1;
use test_db1;
create table t1(f1 int);
create table t2 (f1 int);
insert into t1 values (1), (2), (3), (4), (5);
insert into t2 values (1), (2), (3), (4), (5);

-- more
-- https://www.cloudera.com/documentation/enterprise/5-15-x/topics/sg_hive_sql.html
show current roles;
show role grant group hive;
show grant role r_admin;
show grant role r_etl on database yxt;

-- grant privileges to role r_dev
grant select on database elearning to role r_dev;
grant select on database test_db1 to role r_dev;
grant select on database yxt_dirty, database yxt_gz  to role r_dev;
grant select on database yxt_dirty to role r_dev;
grant select on database yxt_gz to role r_dev;
grant select on database yxt_orc to role r_dev;
grant select on database yxt_parquet to role r_dev;

-- grant privileges to role r_prod
grant select on database elearning to role r_prod;
grant select on database test_db1 to role r_prod;
grant select on database yxt_dirty, database yxt_gz  to role r_prod;
grant select on database yxt_dirty to role r_prod;
grant select on database yxt_gz to role r_prod;
grant select on database yxt_orc to role r_prod;
grant select on database yxt_parquet to role r_prod;

-- kylin integration
ansible ydc -m shell -a 'groupadd g_kylin'
ansible ydc -m shell -a 'mkdir /ws.kylin'
ansible ydc -m shell -a 'adduser u_kylin -g g_kylin -d /ws.kylin'

kinit -kt /cdh.kerberos.sentry/hdfs.keytab hdfs
hdfs dfs -mkdir /ws.kylin
hdfs dfs -chown -R u_kylin:g_kylin /ws.kylin

beeline
!connect jdbc:hive2://10.200.70.161:10000/;principal=hive/_HOST@UYDC.COM
create role r_kylin;
grant role r_kylin to group g_kylin;

create database kylin;
grant all on database kylin to role r_kylin;

revoke all on database default from role r_kylin;
revoke role r_kylin from group g_kylin;
-- GRANT <Privilege> ON URIs (HDFS and S3A)
grant all on uri 'hdfs://ydc-162:8020/ws.kylin' to role r_kylin;
create external table ext_t1 (id int) location '/ws.kylin'


-- 后续一些库的设置
alter database eschool1 set owner user hive;
describe database eschool1;

create database eschool1;
create database elcustom;
create database elearning_delete;
create database elearning_elcustom;
create database elearning_incremental;
create database elearning_reconcile;
create database precomputation;

grant all on database eschool1 to role r_etl;
grant all on database elcustom to role r_etl;
grant all on database elearning_delete to role r_etl;
grant all on database elearning_elcustom to role r_etl;
grant all on database elearning_incremental to role r_etl;
grant all on database elearning_reconcile to role r_etl;
grant all on database precomputation to role r_etl;

grant select on database eschool1 to role r_dev;
grant select on database elcustom to role r_dev;
grant select on database elearning_delete to role r_dev;
grant select on database elearning_elcustom to role r_dev;
grant select on database elearning_incremental to role r_dev;
grant select on database elearning_reconcile to role r_dev;
grant select on database precomputation to role r_dev;