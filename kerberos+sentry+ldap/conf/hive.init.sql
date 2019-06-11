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