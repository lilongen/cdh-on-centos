#!/usr/bin/env python
# coding: utf-8
#

Env = {
    'newdev': {
        'host': '10.200.70.183',
        'parcels': ['CDH-6.3.2-1.cdh6.3.2.p0.1605554', 'GPLEXTRAS-6.3.2-1.gplextras6.3.2.p0.1605554']
    },
    'dev': {
        'host': '10.200.70.171',
        'parcels': ['CDH-5.14.0-1.cdh5.14.0.p0.24', 'GPLEXTRAS-5.14.0-1.cdh5.14.0.p0.22']
    },
    'prod': {
        'host': '10.200.70.61',
        'parcels': ['CDH-5.14.0-1.cdh5.14.0.p0.24', 'GPLEXTRAS-5.14.0-1.cdh5.14.0.p0.22']
    }
}
envs = '{%s}' % ','.join(list(Env.keys()))
Local_Paths =  [
    f'/opt/cloudera/parcels',
    f'/opt/cloudera/spark.dist.classpath/{envs}',
    f'/opt/cloudera/spark.defaults/{envs}',
    f'/opt/cloudera/hadoop.conf/{envs}',
    f'/opt/cloudera/krb5/{envs}',
    f'/opt/cloudera/keytab/{envs}'
]
Sync = {
    '/etc/spark/conf/classpath.txt': '/opt/cloudera/spark.dist.classpath',
    '/etc/spark/conf/spark-defaults.conf': '/opt/cloudera/spark.defaults',
    '/etc/hadoop/conf/': '/opt/cloudera/hadoop.conf',
    '/etc/krb5.conf': '/opt/cloudera/krb5'
}
Cmds = []


def add_separator():
    Cmds.append('')


def generate_mkdir_cmd():
    for path in Local_Paths:
        Cmds.append(f'mkdir -p {path}')
    add_separator()


def generate_rsync_cmds():
    for env, info in Env.items():
        host = info['host']
        for src, dest in Sync.items():
            Cmds.append(f'rsync -avp root@{host}:{src} {dest}/{env}/')
        for parcel in info['parcels']:
            Cmds.append(f'test -d /opt/cloudera/parcels/{parcel} || rsync -avp root@{host}:/opt/cloudera/parcels/{parcel} /opt/cloudera/parcels/')
        
        add_separator()


def ouput_cmds():
    print('\n'.join(Cmds))


def main():
    generate_mkdir_cmd()
    generate_rsync_cmds() 
    ouput_cmds() 


if __name__ == "__main__":
    main()
