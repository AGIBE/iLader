# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os
from iLader.helpers import PostgresHelper
from iLader.helpers import FME_helper

class Transfer2Vek2_PG(TemplateFunction):
    '''
    Kopiert die ÖREBK-Transferstruktur (OEREB2) nach vek2 (PostgreSQL). Es werden nur diejenigen Teile der
    Transferstruktur kopiert, die zum importierten Geoprodukt gehören.
    Wenn zu diesem Geoprodukt keine ÖREBK-Tickets gefunden wurden, wird die ÖREBK-
    Transferstruktur gar nicht kopiert.
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Transfer2Vek2_PG"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgefuehrt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Fuehrt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("ÖREBK-Transferstruktur (OEREB2) wird nach vek2 (PostgreSQL) kopiert.")
        source_connection = self.task_config['connections']['sde_conn_team_oereb2']
        oereb_tables = self.task_config['oereb']['tabellen']
        liefereinheiten = self.task_config['oereb']['liefereinheiten']
        fme_script = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + "\\helpers\\" + "EsriGeodatabase2PostGIS.fmw"
        
        if liefereinheiten == '':
            self.logger.info('Für diesen Import konnten keine ÖREBK-Liefereinheiten ermittelt werden.')
            self.logger.info('Die ÖREBK-Transferstruktur wird daher nicht importiert.')
        else:
            username = self.task_config['schema']['oereb2']
            schema = username
            pw = self.task_config['users']['oereb2']
            db = self.task_config['instances']['vek2']
            port = self.task_config['port_pg']
            host = self.task_config['instances']['oereb']
            for oereb_table in oereb_tables:
                oereb_tablename = oereb_table['tablename']
                oereb_table_filter_field = oereb_table['filter_field']
                
                oereb_delete_sql = "DELETE FROM %s WHERE %s IN %s" % (oereb_tablename, oereb_table_filter_field, liefereinheiten)
                self.logger.info("Deleting...")
                self.logger.info(oereb_delete_sql)
                PostgresHelper.db_sql(self, host, db, username, port, pw, oereb_delete_sql)
                
                source = os.path.join(source_connection, username + "." + oereb_tablename)
                source_layer = username + "." + oereb_tablename
                target_table = (username + "." + oereb_tablename).lower()
                where_clause = oereb_table_filter_field + " IN " + liefereinheiten
                self.logger.info("WHERE-Clause: " + where_clause)
                    
                self.logger.info("Appending...")
                fme_logfile = FME_helper.prepare_fme_log(fme_script, (self.task_config['log_file']).rsplit('\\',1)[0])
                # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
                # Daher müssen workspace und parameters umgewandelt werden!
                parameters = {
                    'TABELLEN': str(source_layer),
                    'POSTGIS_DB': str(db),
                    'POSTGIS_HOST': str(host),
                    'POSTGIS_PORT': str(port),
                    'POSTGIS_USER': str(username),
                    'POSTGIS_PASSWORD': str(pw),
                    'SCHEMA_NAME': str(schema),
                    'LOGFILE': str(fme_logfile),
                    'INPUT_SDE': str(source_connection),
                    'TABLE_HANDLING': "USE_EXISTING",
                    'GEODATABASE_SDE_IN_WHERE': str(where_clause)
                }
                # FME-Skript starten
                FME_helper.fme_runner(self, str(fme_script), parameters)
                                        
                # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
                source_count = int(arcpy.GetCount_management(source)[0])
                self.logger.info("Anzahl Features im Quell-Layer: " + unicode(source_count))
                sql_query = 'SELECT COUNT(*) FROM ' + target_table
                target_count = PostgresHelper.db_sql(self, host, db, username, port, pw, sql_query, True)
                self.logger.info("Anzahl Features im Ziel-Layer: " + unicode(target_count))
                if source_count!=target_count:
                    self.logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
                    raise Exception
                
                self.logger.info("Die Tabelle " + oereb_tablename + " wurde kopiert.")
                        
            self.logger.info("Die ÖREBK-Transferstruktur (OEREB2) wurde kopiert nach vek2 (PostgreSQL) kopiert.")       
            self.finish()