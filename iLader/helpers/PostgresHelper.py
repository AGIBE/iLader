import psycopg2
import sys


def db_sql(host, db, db_user, port, pw, sql_query, fetch=False):
    conn_string = "host='" + host + "' dbname='" + db + "' port ='" + port + "' user='" + db_user + "' password='" + pw + "'"
 
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
    except psycopg2.DatabaseError as ex:
        #TODO: Normale logger Info absetzen
        print("Verbindung zu PostgreSQL " + db + " konnte nicht aufgebaut werden!")
        print(ex)
        print("Import wird abgebrochen!")
        sys.exit()
        
    # execute our Query
    cursor.execute(sql_query)
 
    # retrieve the records from the database
    if fetch:
        records = cursor.fetchone()[0]
    else:
        conn.commit()
    
    cursor.close()
    conn.close()

    if fetch:
        return records