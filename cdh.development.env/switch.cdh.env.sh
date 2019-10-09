#!/usr/bin/env bash
#

to=$1

spark_dist_classpath_file="/opt/cloudera/spark.dist.classpath/${to}/classpath.txt"
spark_defaults_file="/opt/cloudera/spark.defaults/${to}/spark-defaults.conf"
hadoop_conf_dir="/opt/cloudera/hadoop.conf/${to}"

declare -A cdh_parcels 
cdh_parcels=( \
    ["test"]="/opt/cloudera/parcels/CDH-6.3.0-1.cdh6.3.0.p0.1279813" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24" \
)
cdh_parcel=${cdh_parcels[$to]}

echo_ln_cdh() {
    echo ln -sf ${cdh_parcel} /opt/cloudera/parcels/CDH
}

# 1. set JVM_D_JAVA_SECURITY_KRB5_CONF=-Djava.security.krb5.conf=/path/to/krb5.conf
# 2. inject ${JVM_D_JAVA_SECURITY_KRB5_CONF} into spark-submit shell
# 3. ${JVM_D_JAVA_SECURITY_KRB5_CONF} export in echo_env_exports 
echo_inject_jvmd_krb5conf_to_spark_submit() {
    spark_submit_file="${cdh_parcel}/lib/spark/bin/spark-submit"
    echo "grep JVM_D_JAVA_SECURITY_KRB5_CONF ${spark_submit_file} &>/dev/null \
        || perl -i -pE 's|(/bin/spark-class).+(org.apache.spark.deploy.SparkSubmit)|\${1} \\\${JVM_D_JAVA_SECURITY_KRB5_CONF} \${2}|m' ${spark_submit_file}"
}

echo_env_exports() {
    spark_dist_classpath="$(paste -sd: ${spark_dist_classpath_file})"
    spark_yarn_jar=$(grep spark.yarn.jar ${spark_defaults_file} | awk -F'=' '{print $2}')
    krb5_conf_file="/opt/cloudera/krb5/${to}/krb5.conf"
    echo export HADOOP_CONF_DIR=\"${hadoop_conf_dir}\"
    echo export PATH=\"${cdh_parcel}/bin:$PATH\"
    echo export SPARK_DEFAULTS=\"${spark_defaults_file}\"
    echo export SPARK_YARN_JAR=\"$spark_yarn_jar\"
    echo export SPARK_DIST_CLASSPATH=\"$spark_dist_classpath\"
    echo export KRB5_CONFIG=\"${krb5_conf_file}\"
    
    # Why need JVM_D_JAVA_SECURITY_KRB5_CONF? 
    # 1). spark-submit, can not using environment variable KRB5_CONFIG
    # 2). spark-submit -> java ...
    # 3). append -Djava.security.krb5.conf=/path/to/krb5.conf into spark-submit command
    echo export JVM_D_JAVA_SECURITY_KRB5_CONF=\"-Djava.security.krb5.conf=${krb5_conf_file}\"
}

echo_kinit() {
    echo kinit -kt /opt/cloudera/keytab/$to/lile.keytab lile
}

main() {
#    echo_ln_cdh
    echo_env_exports
    echo_inject_jvmd_krb5conf_to_spark_submit
    echo_kinit
}

main
