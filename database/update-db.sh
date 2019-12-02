# to update database

# grab the files and adds them to mysql-scripts
./get-production-db.sh

# append to the top of the file
printf "Updating iptLocal database...\n"
echo 'DROP DATABASE IF EXISTS `iptLocal`;\nCREATE DATABASE  IF NOT EXISTS `iptLocal` /*!40100 DEFAULT CHARACTER SET latin1 */;\nUSE `iptLocal`;' | \
        cat - ./mysql-scripts/iptProduction.sql > temp && mv temp ./mysql-scripts/iptProduction.sql

# mysql --defaults-group-suffix=local < /database/mysql-scripts/dockEventsStaging.sql

status=$?

if [ "$status" -eq "0" ]; then
    
    pv ./mysql-scripts/iptProduction.sql | mysql --defaults-group-suffix=local
    printf "Update Complete!\n"
else
    printf "FAILLED!!!"
    exit 1
fi 

exit $status