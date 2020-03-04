##### before cloudera manager setup web guide
High Recommended: Pre-Install cloudera-manager-agent and all dependencied of cloudera-manager-agent will keep cloudera-manager-agent setup will successfully on all nodes, otherwise on CM first step , all nodes will simultaneously query inner yum repo to get dependencies, and download dependencies from internet(outside), it has very high probablility failed on first step-setup CM-agent on all nodes

##### make kdc server ready
https://gist.github.com/lilongen/fc3bbaf55ba403820a5632d42920f4cc

##### CDH cluster deployment

#### CDH LZO install - GPL Extra Parcels
guide: https://www.cnblogs.com/zhzhang/p/5695027.html
archive location: https://archive.cloudera.com/gplextras6/
1. config LZO parcels
2. install, distribute and activate LZO parcels
3. hdfs configure changes
a. 在io.compression.codecs属性值中追加如下值：
   com.hadoop.compression.lzo.LzoCodec
   com.hadoop.compression.lzo.LzopCodec
4. 修改YARN配置
   将mapreduce.application.classpath的属性值增加一项：/opt/cloudera/parcels/HADOOP_LZO/lib/hadoop/lib/*
   /opt/cloudera/parcels/GPLEXTRAS/lib/hadoop/lib/hadoop-lzo.jar

##### add sentry service
https://blog.51cto.com/14049791/2320241

##### enable kerberos 

##### configure hdfs, hive, impala, hue 使用 sentry
https://blog.51cto.com/14049791/2320241
###### hdfs
1. 开启ACLs, Enable Access Control Lists, dfs.namenode.acls.enabled
2. 启用sentry同步, Enable Sentry Synchronization
###### hive
1. 配置Hive使用Sentry服务, sentry service
2. 关闭Hive的用户模拟功能, HiveServer2 Enable Impersonation
hive.server2.enable.impersonation, hive.server2.enable.doAs
3. Enable Stored Notifications in Database - Enable stored notifications of metadata changes. When enabled, each metadata change will be stored in NOTIFICATION_LOG
###### impala
1. 配置impala使用Sentry服务, sentry service
###### hue
1. 配置hue使用Sentry服务, sentry service
2. configure ldap 
https://cloud.tencent.com/developer/article/1357110

##### user/group/role的配置
https://blog.51cto.com/14049791/2320241


##### ssl certificate if enable ssl, hdfs, hive, hbase
```bash
openssl genrsa -out lile.ca.key 1024
openssl req -new -x509 -key lile.ca.key -out lile.ca.crt -subj /C=CN/ST=JiangSu/L=SuZhou/O=YXT/OU=BDAI/CN=BDAI_CA/ -days 3650 -set_serial 1
openssl genrsa -out ydc.key 1024
openssl req -new -key ydc.key -out ydc-161.csr -subj '/C=CN/ST=JiangSu/L=SuZhou/O=YXT/OU=BDAI/CN=ydc-161/'
openssl req -new -key ydc.key -out ydc-162.csr -subj '/C=CN/ST=JiangSu/L=SuZhou/O=YXT/OU=BDAI/CN=ydc-162/'
openssl req -new -key ydc.key -out ydc.csr -subj '/C=CN/ST=JiangSu/L=SuZhou/O=YXT/OU=BDAI/CN=ydc-*/'
openssl x509 -req -in ydc.csr -out ydc.crt -CA lile.ca.crt -CAkey lile.ca.key -days 3650 -set_serial 10
openssl x509 -req -in ydc-161.csr -out ydc-161.crt -CA lile.ca.crt -CAkey lile.ca.key -days 3650 -set_serial 11
openssl x509 -req -in ydc-162.csr -out ydc-162.crt -CA lile.ca.crt -CAkey lile.ca.key -days 3650 -set_serial 12
```

##### hue ldap
###### issue: 6.3.2 hue 
ldap "user_filter" is set, can not authenticate, pop error in /opt/cloudera/parcels/CDH-6.3.2-1.cdh6.3.2.p0.1605554/lib/hue/desktop/core/src/desktop/auth/forms.py forms.py
so just keep user_filter unset

###### vim /etc/hue/conf/log.conf to set hue error log detail file path and file name 
to get more detail error info
```
[formatter_default]
class=desktop.log.formatter.Formatter
#format=[%(asctime)s] %(module)-12s %(levelname)-8s %(message)s
format=[%(asctime)s] %(pathname)s %(filename)s [line:%(lineno)d] %(module)-12s %(levelname)-8s %(message)s
datefmt=%d/%b/%Y %H:%M:%S %z
```

###### bind_dn include 中文出错的workaround
```python
File "/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/lib/hue/build/env/lib/python2.7/site-packages/django_auth_ldap-1.2.0-py2.7.egg/django_auth_ldap/config.py", line 159, in execute
    filterstr = self.filterstr % filterargs
UnicodeDecodeError: 'ascii' codec can't decode byte 0xe7 in position 73: ordinal not in range(128)

solution/
file: 
/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/lib/hue/build/env/lib/python2.7/site-packages/django_auth_ldap-1.2.0-py2.7.egg/django_auth_ldap/config.py
line 155:
            filterstr = self.filterstr % filterargs
    to
            # added for workaround hue ldap login issue
            # 2019/05/23, lile
            for k, v in filterargs.items():
                if isinstance(v, unicode):
                    filterargs[k] = v.encode('utf-8')
            # end
            filterstr = self.filterstr % filterargs
            
line 217-219: commented
        #logger.debug(u"search_s('%s', %d, '%s') returned %d objects: %s" %
        #             (self.base_dn, self.scope, self.filterstr, len(result_dns),
# "; ".join(result_dns)))
```

##### krb5.conf 
```ini
[libdefaults]
 default_realm = UYDC.COM
 dns_lookup_realm = false
 dns_lookup_kdc = false
 ticket_lifetime = 24h
 renew_lifetime = 7d
 forwardable = true
 rdns = false
 # Importatnt !!!
 # use default_ccache_name = FILE:/tmp/krb5cc_%{uid} to
 # make beeline, hdfs, hbase shell can get kerberos ticket
 # otherwise beeline, hdfs, hbase .. shell will throw can not get kerberos ticket error
 #
 #default_ccache_name KEYRING:persistent:%{uid}
 default_ccache_name = FILE:/tmp/krb5cc_%{uid}
```

##### kerberos addprinc: hdfs, hive, hbase, impala
```bash
kadmin -p root/admin -w $kadmin_pwd addprinc -pw lle hdfs
kadmin -p root/admin -w $kadmin_pwd ktadd -k /cdh.kerberos.sentry/hdfs.keytab hdfs
kadmin -p root/admin -w $kadmin_pwd addprinc -pw lle hive
kadmin -p root/admin -w $kadmin_pwd ktadd -k /cdh.kerberos.sentry/hive.keytab hive
kadmin -p root/admin -w $kadmin_pwd addprinc -pw lle impala
kadmin -p root/admin -w $kadmin_pwd ktadd -k /cdh.kerberos.sentry/impala.keytab impala
kadmin -p root/admin -w $kadmin_pwd addprinc -pw lle hbase
kadmin -p root/admin -w $kadmin_pwd ktadd -k /cdh.kerberos.sentry/hbase.keytab hbase
```

##### hive beeline create admin role and grant admin role to hive group
```
#beeline
> !connect jdbc:hive2://localhost:10000/;principal=hive/_HOST@UYDC.COM

create role r_admin;
grant all on server server1 to role r_admin;
grant role r_admin to group hive;

```


##### Copying Data between a Secure and an Insecure Cluster using DistCp and WebHDFS 
https://www.cloudera.com/documentation/enterprise/5-14-x/topics/cdh_admin_distcp_secure_insecure.html#xd_583c10bfdbd326ba-7dae4aa6-147c30d0933--7c49