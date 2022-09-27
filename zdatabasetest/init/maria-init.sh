mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD"
    BEGIN;
        CREATE DATABASE dbaasservice;
        CREATE DATABASE scheduleservice;
    COMMIT;
EOSQL 