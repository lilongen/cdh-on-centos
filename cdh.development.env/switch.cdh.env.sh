#!/usr/local/bin/bash

declare -A path_appendix 
path_appendix=( \
    ["test"]="/opt/cloudera/parcels/CDH-6.3.0-1.cdh6.3.0.p0.1279813" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24" \
)

declare -A spark_yarn_jar
spark_yarn_jar=( \
    ["test"]="/opt/cloudera/parcels/CDH-6.3.0-1.cdh6.3.0.p0.1279813/lib/spark/jars/spark-yarn_2.11-2.4.0-cdh6.3.0.jar" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/lib/spark/lib/spark-assembly.jar" \
    ["dev"]="/opt/cloudera/parcels/CDH-5.14.0-1.cdh5.14.0.p0.24/lib/spark/lib/spark-assembly.jar" \
)

declare -A spark_dist_classpath
spark_dist_classpath=( \
    ["test"]="/opt/cloudera/spark.dist.classpath/test.classpath.txt" \
    ["dev"]="/opt/cloudera/spark.dist.classpath/dev.classpath.txt" \
    ["prod"]="/opt/cloudera/spark.dist.classpath/prod.classpath.txt" \
)

declare -A hadoop_conf
hadoop_conf=( \
    ["test"]="/opt/cloudera/hadoop.conf/test" \
    ["dev"]="/opt/cloudera/hadoop.conf/dev" \
    ["prod"]="/opt/cloudera/hadoop.conf/prod" \
)

switch() {
    to=$1
    export HADOOP_CONF_DIR="${hadoop_conf[$to]}"
    export SPARK_DIST_CLASSPATH==$(paste -sd: "${spark_dist_classpath[$to]}")
    export PATH="${path_appendix[$to]}:$PATH"
    export SPARK_YARN_JAR="${spark_yarn_jar[$to]}"
}

switch $1
env
