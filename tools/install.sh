#/bin/sh
if [ $# -ne 1 ]
then
    echo "Usage: `basename $0` ol|demo"
    exit -1
fi

arg=$1
host=""
hostname=`hostname`

if [ $arg = "ol" ]
then
    host=`hostname|awk -F '.' '{print $3}'`
elif [ $arg = "A" ] || [ $arg = "B" ]
then
    host=`hostname|awk -F '.' '{print $3}'`.$arg
elif [ $arg = "demo" ]
then
    host="demo"
else
    echo "Usage: `basename $0` ol|demo"
    exit -1
fi


# etc
#ln -sf /home/s/apps/CloudSearch/asynchronous_application_python/etc/config.$host  /home/s/apps/CloudSearch/asynchronous_application_python/etc/qrec_server.conf


