# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

def get_old_statistics(connection):
    index_tables_sql = "select table_name from USER_TAB_STATISTICS where table_name not like '%_IDX$%' and (stale_stats='YES' or stale_stats is null)" 
    index_tables_result = connection.db_read(index_tables_sql)
    index_tables = [index_table[0] for index_table in index_tables_result]
    return index_tables
    
def get_indexes_of_table(indexed_table, connection):
    indexes_sql = "select index_name from USER_INDEXES where table_name='%s' and index_type='NORMAL'" % (indexed_table)
    indexes_result = connection.db_read(indexes_sql)
    indexes = [index[0] for index in indexes_result]
    return indexes
    
def renew_statistics(connection):
    '''
    Die Funktion wird nach dem Reinladen (Ersatz oder Neu) von Daten im Vek1, Vek2 und Vek3 ausgeführt. So dass Statistiken jeweils aktuell sind, insbesondere auch für tagesaktuelle Geoprodukte.
    '''
    index_tables = get_old_statistics(connection)
    
    for index_table in index_tables:
        # alle Indices rebuilden (ausser Spatial Index und LOB-Index)
        indexes = get_indexes_of_table(index_table,connection)
        for index in indexes:
            index_sql = "ALTER INDEX " + index + " REBUILD"
            connection.db_write(index_sql)

        connection.db_callproc('dbms_stats.delete_table_stats', [connection.username, index_table])
        connection.db_callproc('dbms_stats.gather_table_stats', [connection.username, index_table])
    return 'OK'