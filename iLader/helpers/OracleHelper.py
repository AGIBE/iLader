# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle

def readOracleSQL(db, username, password, sql, fetchall=True):
    with cx_Oracle.connect(username, password, db) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        if fetchall:
            result = cur.fetchall()
        else:
            result = cur.fetchone()
    
    return result

def writeOracleSQL_check(self, db, username, password, sql, msg_err, excep=True):
    with cx_Oracle.connect(username, password, db) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        
        if cur.rowcount == 1:
            # Nur wenn genau 1 Zeile aktualisiert wurde, ist alles i.O. 
            self.logger.info("Query wurde ausgeführt!")
        else:
            # Wenn nicht genau 1 Zeile aktualisiert wurde, muss abgebrochen werden
            self.logger.error("Query wurde nicht erfolgreich ausgeführt.")
            self.logger.error(msg_err)
            if excep:
                raise Exception

def writeOracleSQL(db, username, password, sql):
    # Mit dem With-Statement wird sowohl committed als auch die
    # Connection- und Cursor-Objekte automatisch geschlossen
    with cx_Oracle.connect(username, password, db) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
   
def writeOracleSQL_multiple(db, username, password, sql):
    with cx_Oracle.connect(username, password, db) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        for sql_statement in sql:
            cur.execute(sql_statement)
 
