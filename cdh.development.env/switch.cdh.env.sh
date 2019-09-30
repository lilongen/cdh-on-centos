#!/usr/bin/env bash

to=$1

spark_dist_classpath_file="/opt/cloudera/spark.dist.classpath/${to}/classpath.txt"
spark_defaults_file="/opt/cloudera/spark.defaults/${to}/spark-defaults.conf"
hadoop_conf_dir="/opt/cloudera/hadoop.conf/${to}"

declare -A path_appendix 
path_appendix=( \
    ["test"]="/opt/cloudera/parcels/CDH-6.3.0-1.cdh6.3.0.p0.1279813/bin" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/bin" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/bin" \
)

echo_ln_cdh() {
    bin_path=${path_appendix[$to]}
    cdh_path=${bin_path:0:-4}
    echo ln -sf $cdh_path /opt/cloudera/parcels/CDH
}

echo_env_exports() {
    spark_dist_classpath="$(paste -sd: ${spark_dist_classpath_file})"
    spark_yarn_jar=$(grep spark.yarn.jar ${spark_defaults_file} | awk -F'=' '{print $2}')
    echo export HADOOP_CONF_DIR=\"${hadoop_conf_dir}\"
    echo export PATH=\"${path_appendix[$to]}:$PATH\"
    echo export SPARK_YARN_JAR=\"$spark_yarn_jar\"
    echo export SPARK_DIST_CLASSPATH=\"$spark_dist_classpath\"
}

echo_lnkrb5conf_and_kinit() {
    echo sudo ln -sf /opt/cloudera/krb5/$to/krb5.conf /etc/krb5.conf
    echo kinit -kt /opt/cloudera/keytab/$to/lile.keytab lile
}

main() {
    echo_ln_cdh
    echo_env_exports
    echo_lnkrb5conf_and_kinit
}

main
