#!/usr/bin/env bash
to=$1

declare -A path_appendix 
path_appendix=( \
    ["test"]="/opt/cloudera/parcels/CDH-6.3.0-1.cdh6.3.0.p0.1279813/bin" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/bin" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/bin" \
)

declare -A hadoop_conf
hadoop_conf=( \
    ["test"]="/opt/cloudera/hadoop.conf/test" \
    ["dev"]="/opt/cloudera/hadoop.conf/dev" \
    ["prod"]="/opt/cloudera/hadoop.conf/prod" \
)

echo_env_export() {
    spark_dist_classpath_file="/opt/cloudera/spark.dist.classpath/${to}/classpath.txt"
    spark_dist_classpath="$(paste -sd: ${spark_dist_classpath_file})"

    spark_defaults_file="/opt/cloudera/spark.defaults/${to}/spark-defaults.conf"
    spark_yarn_jar=$(grep spark.yarn.jar ${spark_defaults_file} | awk -F'=' '{print $2}')

    echo export HADOOP_CONF_DIR=\"${hadoop_conf[$to]}\"
    echo export PATH=\"${path_appendix[$to]}:$PATH\"
    echo export SPARK_YARN_JAR=\"$spark_yarn_jar\"
    echo export SPARK_DIST_CLASSPATH=\"$spark_dist_classpath\"
}

echo_krb5_init() {
    echo sudo ln -sf /opt/cloudera/krb5/$to/krb5.conf /etc/krb5.conf
    echo kinit -kt /opt/cloudera/keytab/$to/lile.keytab lile
}

swicth() {
    echo_env_export
    echo_krb5_init
}

swicth
