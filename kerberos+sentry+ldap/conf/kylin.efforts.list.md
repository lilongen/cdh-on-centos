ansible ydc -m shell -a 'groupadd g_kylin'
ansible ydc -m shell -a 'adduser u_kylin -g g_kylin -d /ws.kylin'

# https://www.tutorialspoint.com/hbase/hbase_security.htm
privilege:
    R - represents read privilege.
    W - represents write privilege.
    X - represents execute privilege.
    C - represents create privilege.
    A - represents admin privilege.

hbase shell:
grant 'u_kylin',  'RWXC', '@default' # user u_kylin
grant 'u_kylin',  'RWXC', '@ns_x' # user u_kylin
grant '@g_kylin', 'RWXC', '@default' # group g_kylin
grant '@g_kylin', 'RWXC', '@ns_x' # group g_kylin
grant '@g_kylin', 'RWXC', '@ns_x.tbl_y' # group g_kylin

# https://www.cloudera.com/documentation/enterprise/latest/topics/sg_hive_sql.html#grant_privilege_on_uri
grant all on uri 'hdfs://ydc-162:8020/ws.kylin' to role r_kylin;
create external table ext_t1 (id int) location '/ws.kylin'

revoke 'u_kylin'
revoke '@g_kylin'
revoke '@g_kylin', '@default'
