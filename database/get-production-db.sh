printf "Dumping iptProduction Database to ./mysql-scripts...\n"
mysqldump --defaults-group-suffix=production \
            --where="1 limit 50" \
            --set-gtid-purged=OFF \
            iptProduction | pv -W > ./mysql-scripts/iptProduction.sql

status=$?

if [ "$status" -eq "0" ]; then
    printf "Dumped Successfully!\n"

else
    printf "Dump failed\n"
    exit 1
fi 


exit $status