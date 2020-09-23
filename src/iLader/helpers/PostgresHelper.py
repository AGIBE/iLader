# -*- coding: utf-8 -*-
import psycopg2
import sys


def db_sql(self, host, db, db_user, port, pw, sql_query, fetch=False, fetchall=False):
    conn_string = "host='" + host + "' dbname='" + db + "' port ='" + port + "' user='" + db_user + "' password='" + pw + "'"
 
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
    except psycopg2.DatabaseError as ex:
        self.logger.error("Verbindung zu PostgreSQL " + db + " konnte nicht aufgebaut werden!")
        self.logger.error(ex)
        self.logger.error("Import wird abgebrochen!")
        sys.exit()
        
    # execute Query
    cursor.execute(sql_query)
 
    # retrieve all or one records from the database or commit
    if fetch:
        if fetchall:
            records = cursor.fetchall()
        else:
            records = cursor.fetchone()
            if records:
                records = records[0]
    else:
        conn.commit()
    
    cursor.close()
    conn.close()

    if fetch:
        return records