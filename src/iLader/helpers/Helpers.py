# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
from iLader.__init__ import __version__  
import os
import csv
import getpass
import datetime
import psycopg2
import tempfile
import sys
import arcpy

def get_config(create_connection_files=True):
    config = AGILib.Configuration(configfile_envvar='GEODBIMPORTHOME').config
    connection_infos = AGILib.Configuration(configfile_path=config['agilib_connections']).config
    connections = {}
    connection_files = {}
    # Alle benötigten Connections und Connection-Files erstellen
    # Oracle
    #VEK1
    connections['VEK1_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['vek1']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    connections['VEK1_GEO_ORA'] = AGILib.Connection(db=connection_infos['db']['vek1']['ora_db'], db_type='oracle', username=connection_infos['user']['geo']['username'], password=connection_infos['user']['geo']['password'])
    connections['VEK1_OEREB2_ORA'] = AGILib.Connection(db=connection_infos['db']['vek1']['ora_db'], db_type='oracle', username=connection_infos['user']['oereb2']['username'], password=connection_infos['user']['oereb2']['password'])
    
    #VEK2
    connections['VEK2_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['vek2']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    connections['VEK2_GEO_ORA'] = AGILib.Connection(db=connection_infos['db']['vek2']['ora_db'], db_type='oracle', username=connection_infos['user']['geo']['username'], password=connection_infos['user']['geo']['password'])
    connections['VEK2_OEREB2_ORA'] = AGILib.Connection(db=connection_infos['db']['vek2']['ora_db'], db_type='oracle', username=connection_infos['user']['oereb2']['username'], password=connection_infos['user']['oereb2']['password'])
    
    #VEK3
    connections['VEK3_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['vek3']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    connections['VEK3_GEO_ORA'] = AGILib.Connection(db=connection_infos['db']['vek3']['ora_db'], db_type='oracle', username=connection_infos['user']['geo']['username'], password=connection_infos['user']['geo']['password'])
    
    #RAS1
    connections['RAS1_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['ras1']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    connections['RAS1_GEO_ORA'] = AGILib.Connection(db=connection_infos['db']['ras1']['ora_db'], db_type='oracle', username=connection_infos['user']['geo']['username'], password=connection_infos['user']['geo']['password'])
    
    #RAS2
    connections['RAS2_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['ras2']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    
    #TEAM
    connections['TEAM_GEODB_DD_ORA'] = AGILib.Connection(db=connection_infos['db']['team']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb_dd']['username'], password=connection_infos['user']['geodb_dd']['password'])
    connections['TEAM_NORM_ORA'] = AGILib.Connection(db=connection_infos['db']['team']['ora_db'], db_type='oracle', username=connection_infos['user']['norm']['username'], password=connection_infos['user']['norm']['password'])
    connections['TEAM_OEREB2_ORA'] = AGILib.Connection(db=connection_infos['db']['team']['ora_db'], db_type='oracle', username=connection_infos['user']['oereb2']['username'], password=connection_infos['user']['oereb2']['password'])
    
    #WORK
    connections['WORK_GDBP_ORA'] = AGILib.Connection(db=connection_infos['db']['work']['ora_db'], db_type='oracle', username=connection_infos['user']['gdbp']['username'], password=connection_infos['user']['gdbp']['password'])

    if create_connection_files:
        connection_files['VEK1_GEODB_ORA'] = connections['VEK1_GEODB_ORA'].create_sde_connection()
        connection_files['VEK1_GEO_ORA'] = connections['VEK1_GEO_ORA'].create_sde_connection()
        connection_files['VEK1_OEREB2_ORA'] = connections['VEK1_OEREB2_ORA'].create_sde_connection()
        connection_files['VEK2_GEODB_ORA'] = connections['VEK2_GEODB_ORA'].create_sde_connection()
        connection_files['VEK2_GEO_ORA'] = connections['VEK2_GEO_ORA'].create_sde_connection()
        connection_files['VEK2_OEREB2_ORA'] = connections['VEK2_OEREB2_ORA'].create_sde_connection()
        connection_files['VEK3_GEODB_ORA'] = connections['VEK3_GEODB_ORA'].create_sde_connection()
        connection_files['VEK3_GEO_ORA'] = connections['VEK3_GEO_ORA'].create_sde_connection()
        connection_files['RAS1_GEODB_ORA'] = connections['RAS1_GEODB_ORA'].create_sde_connection()
        connection_files['RAS1_GEO_ORA'] = connections['RAS1_GEO_ORA'].create_sde_connection()
        connection_files['RAS2_GEODB_ORA'] = connections['RAS2_GEODB_ORA'].create_sde_connection()
        connection_files['TEAM_NORM_ORA'] = connections['TEAM_NORM_ORA'].create_sde_connection()
        connection_files['TEAM_OEREB2_ORA'] = connections['TEAM_OEREB2_ORA'].create_sde_connection()
    
    #PostgreSQL
    connections['VEK1_GEODB_PG'] = AGILib.Connection(db=connection_infos['db']['vek1']['pg_db'], db_type='postgres', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'], host=connection_infos['db']['vek1']['pg_host'], port=connection_infos['db']['vek1']['pg_port'])    
    connections['VEK2_GEODB_PG'] = AGILib.Connection(db=connection_infos['db']['vek2']['pg_db'], db_type='postgres', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'], host=connection_infos['db']['vek2']['pg_host'], port=connection_infos['db']['vek2']['pg_port'])
    connections['VEK1_OEREB_PG'] = AGILib.Connection(db=connection_infos['db']['vek1']['pg_db'], db_type='postgres', username=connection_infos['user']['oereb']['username'], password=connection_infos['user']['oereb']['password'], host=connection_infos['db']['vek1']['pg_host'], port=connection_infos['db']['vek1']['pg_port'])
    connections['VEK2_OEREB_PG'] = AGILib.Connection(db=connection_infos['db']['vek2']['pg_db'], db_type='postgres', username=connection_infos['user']['oereb']['username'], password=connection_infos['user']['oereb']['password'], host=connection_infos['db']['vek2']['pg_host'], port=connection_infos['db']['vek2']['pg_port'])
    connections['TEAM_OEREB_PG'] = AGILib.Connection(db=connection_infos['db']['team']['pg_db'], db_type='postgres', username=connection_infos['user']['oereb']['username'], password=connection_infos['user']['oereb']['password'], host=connection_infos['db']['team']['pg_host'], port=connection_infos['db']['team']['pg_port'])
    connections['WORK_OEREB_PG'] = AGILib.Connection(db=connection_infos['db']['work']['pg_db'], db_type='postgres', username=connection_infos['user']['oereb']['username'], password=connection_infos['user']['oereb']['password'], host=connection_infos['db']['work']['pg_host'], port=connection_infos['db']['work']['pg_port'])

    config['connections'] = connections
    config['connection_files'] = connection_files
    return config

def register_installations(general_config, logger):
    '''
    Legt die installierte Version inkl. Angabe zu User und PC zentral in csv-Datei ab.
    '''
    try:
        instfile = general_config['INSTALLATION']['instreg']
        usrlist = []
        usr = getpass.getuser()
        pc = os.environ['COMPUTERNAME']
        # csv einlesen
        with open(instfile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=str(u';'))
            for row in spamreader:
                usrlist.append([row[0], row[1], row[2]])
        # csv allenfalls ergaenzen
        if not [__version__, usr, pc] in usrlist:
            with open(instfile, 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=str(u';'))
                spamwriter.writerow([__version__ , usr, pc, datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")])
    except Exception as e:
        logger.warn('Installationsversion konnte nicht zentral abgelegt werden. ' + e)
        pass

    
def get_import_tasks():
    tasks = []

    general_config = get_config(create_connection_files=True)

    import_tasks_sql = "SELECT t.TASK_OBJECTID, u.UC_BEZEICHNUNG, g.GPR_BEZEICHNUNG, z.GZS_JAHR, z.GZS_VERSION FROM TB_TASK t LEFT JOIN TB_USECASE u ON t.UC_OBJECTID=u.UC_OBJECTID LEFT JOIN TB_GEOPRODUKT_ZEITSTAND z ON z.GZS_OBJECTID = t.GZS_OBJECTID LEFT JOIN TB_GEOPRODUKT g ON z.GPR_OBJECTID = g.GPR_OBJECTID WHERE t.TASK_STATUS=1 ORDER BY g.GPR_BEZEICHNUNG ASC"
    import_tasks_result = general_config['connections']['TEAM_GEODB_DD_ORA'].db_read(import_tasks_sql)
    
    for import_task in import_tasks_result:
        parameter_string = "%s: %s %s_%s (%s)" % (unicode(import_task[0]), import_task[2], unicode(import_task[3]), unicode(import_task[4]), import_task[1])
        tasks.append(parameter_string) 
    
    return tasks

def prepare_fme_log(fme_script, log_directory):
    prefix = os.path.splitext(os.path.basename(fme_script))[0]
    fme_logfilename = prefix + "_fme" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
    fme_logfile = os.path.join(log_directory, fme_logfilename)
    
    return fme_logfile

def oereb_append_transferstruktur(source_connection_string, target_connection_string, source_sql, full_tablename):
    '''
    Wird von den ÖREB-Funktionen verwendet, um die Transferstruktur von einer PostgreSQL-DB
    in die andere zu kopieren. Ist evtl. ein Kandidat für die AGILib.
    '''
    # https://codereview.stackexchange.com/questions/115863/run-query-and-insert-the-result-to-another-table
    # Inhalte aus WORK mit COPY TO in ein Temp-File schreiben
    copy_to_query = "COPY (%s) TO STDOUT WITH (FORMAT text)" % (source_sql)
    with tempfile.NamedTemporaryFile('w+t') as fp:
        with psycopg2.connect(source_connection_string) as source_connection:
            with source_connection.cursor() as source_cursor:
                source_cursor.copy_expert(copy_to_query, fp)

        # Alles ins File rausschreiben
        fp.flush()
        # File auf Anfang zurücksetzen
        fp.seek(0)

        with psycopg2.connect(target_connection_string) as target_connection:
            with target_connection.cursor() as target_cursor:
                target_cursor.copy_from(file=fp, table=full_tablename)

def oereb_copy_transferstruktur(target_connection, general_config, task_config, logger):
    '''
    Kopiert die PostgreSQL-Transferstruktur des ÖREB-Katasters von einer DB in
    die andere.
    '''
    source_connection = general_config['connections']['TEAM_OEREB_PG']
    oereb_pg_tables = task_config['oereb']['tabellen_pg']
    oereb_pg_tables_reversed = oereb_pg_tables[::-1]
    liefereinheiten = task_config['oereb']['liefereinheiten']
    oereb_pg_schemas = task_config['oereb']['schemas']
    
    if liefereinheiten == '()':
        logger.info('Für diesen Import konnten keine ÖREBK-Liefereinheiten ermittelt werden.')
        logger.info('Die ÖREBK-Transferstruktur wird daher nicht importiert.')
    else:
        for schema in oereb_pg_schemas:
            logger.info("Bearbeite Schema %s..." % (schema))
            for oereb_pg_table in oereb_pg_tables:
                full_tablename = schema + "." + oereb_pg_table['tablename']
                where_clause = "%s IN %s" % (oereb_pg_table['filter_field'], liefereinheiten)
                delete_sql = "DELETE FROM %s WHERE %s" % (full_tablename, where_clause) 
                logger.info("Deleting...")
                logger.info(delete_sql)
                target_connection.db_write(delete_sql)

            # Beim Einfügen muss die umgekehrte Tabellen-Reihenfolge als beim Löschen verwendet werden
            # Grund: Foreign Key-Constraints
            logger.info("Appending...")
            for oereb_pg_table in oereb_pg_tables_reversed:
                full_tablename = schema + "." + oereb_pg_table['tablename']
                where_clause = "%s IN %s" % (oereb_pg_table['filter_field'], liefereinheiten)
                count_sql = "SELECT * FROM %s WHERE %s" % (full_tablename, where_clause)
                logger.info(count_sql)
                oereb_append_transferstruktur(source_connection.postgres_connection_string, target_connection.postgres_connection_string, count_sql, full_tablename)
                # QS (Objekte zählen)
                logger.info("Counting..")
                source_count = len(source_connection.db_read(count_sql))
                target_count = len(target_connection.db_read(count_sql))
                logger.info("Anzahl Features im Quell-Layer: " + unicode(source_count))
                logger.info("Anzahl Features im Ziel-Layer: " + unicode(target_count))
                if source_count!=target_count:
                    logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
                    logger.error("Release wird abgebrochen!")
                    sys.exit()
                
                logger.info("Die Tabelle %s wurde kopiert." % (full_tablename))
            logger.info("Das Schema %s wurde kopiert." % (schema))
                    
        logger.info("Die ÖREBK-Transferstruktur PostGIS wurde von team nach %s kopiert." % (target_connection.db))    

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

def create_dummy(source):
    # Dummy-Eintrag in Source erstellen
    arcpy.AddField_management(source, "dummy", "TEXT", field_length = 10)
    dummy_rows = arcpy.InsertCursor(source)
    dummy_row = dummy_rows.newRow()
    dummy_row.setValue("dummy","dummy_text")
    dummy_rows.insertRow(dummy_row)
    del dummy_row
    del dummy_rows

def delete_dummy(source, table, connection):
    # Dummy Eintrag aus Quelle löschen
    arcpy.DeleteField_management(source,["dummy"])
    arcpy.DeleteRows_management(source)
    # Dummy Eintrag aus Ziel löschen
    delete_sql = 'DELETE FROM ' + table
    connection.db_write(delete_sql)          