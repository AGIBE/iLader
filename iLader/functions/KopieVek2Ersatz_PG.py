# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os
from iLader.helpers import fme_helper, PostgresHelper

class KopieVek2Ersatz_PG(TemplateFunction):
    '''
    Kopiert sämtliche Vektorebenen aus der Instanz TEAM in die Instanz vek2 (PostgreSQL). Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz vek2 sind die Ebenen bereits vorhanden und müssen vorgängig
    gelöscht werden.
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["vektor_ebenen"]``
    
    Nach dem Kopiervorgang setzt die Funktion auch noch die korrekten Berechtigungen d.h.
    sie vergibt SELECT-Rechte an eine Rolle. Die Rolle ist in task_config abgelegt:
    
    - ``task_config["rolle"]``
    
    Auf das explizite Berechnen des räumlichen Indexes wird verzichtet.
    '''
    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "KopieVek2Ersatz_PG"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgefuehrt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        rolle = self.task_config['rolle']
        db = self.task_config['db_vek2_pg']
        port = self.task_config['port_pg']
        host = self.task_config['instances']['oereb']
        db_user = 'geodb'
        schema = self.task_config['schema']['geodb']
        pw = self.task_config['users']['geodb']
        source_sde = self.task_config['connections']['sde_conn_norm']
        # TODO: in Variable auslagern
        fme_script = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + "\\helpers\\" + "EsriGeodatabase2PostGIS.fmw"
        
        # Jede Ebene durchgehen
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']       
            source_table = source.rsplit('\\',1)[1]
            table = ebene['ziel_vek2'].rsplit('\\',1)[1]
            ebename = ebene['gpr_ebe'].lower()
            
            self.logger.info("Ebene " + ebename + " wird nach vek2 kopiert.")
            self.logger.info("Quelle: " + source)
            self.logger.info("Ziel: " + host + "/" + db +" "+ table)
            
            # Pruefen ob es die source Tabelle gibt
            if not arcpy.Exists(source):
                # Existiert die Quell-Ebene nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Quell-Ebene " + source + " existiert nicht!")
                raise Exception
#             table_sp = table.split('.')
#             sql_query = "SELECT 1 FROM information_schema.tables WHERE table_schema = '" + table_sp[0] + "' AND table_name = '" + table_sp[1] + "'"
#             result_vek1 = PostgresHelper.db_sql(host, db, db_user, port, pw, sql_query, True)
#             if result_vek1 == 1:
#                 # Gibt es die Ziel-Ebene bereits, muss sie geloescht werden
#                 self.logger.info("Ebene " + target + " wird nun geloescht!")
#                 sql_query = "DROP TABLE " + table
#                 PostgresHelper.db_sql(host, db, db_user, port, pw, sql_query)
                
            # Daten kopieren
            # Copy-Script
            fme_logfile = fme_helper.prepare_fme_log(fme_script, (self.task_config['log_file']).rsplit('\\',1)[0])
            
            # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
            # Daher müssen workspace und parameters umgewandelt werden!
            parameters = {
                'TABELLEN': str(source_table),
                'POSTGIS_DB': str(db),
                'POSTGIS_HOST': str(host),
                'POSTGIS_PORT': str(port),
                'POSTGIS_USER': str(db_user),
                'SCHEMA_NAME': str(schema),
                'POSTGIS_PASSWORD': str(pw),
                'LOGFILE': str(fme_logfile),
                'INPUT_SDE': str(source_sde)
            }
            # FME-Skript starten
            fme_helper.fme_runner(str(fme_script), parameters)
            
            # Berechtigungen setzen
            self.logger.info("Berechtigungen für Ebene " + table + " wird gesetzt: Rolle " + rolle)
            sql_query = 'GRANT SELECT ON ' + table + ' TO ' + rolle
            PostgresHelper.db_sql(host, db, db_user, port, pw, sql_query)
            
            # Set Primary Key
            self.logger.info("Primary Key für Ebene " + table + " wird gesetzt.")
            sql_query = 'ALTER TABLE ' + table + ' ADD CONSTRAINT ' + ebename + '_objectid_pk PRIMARY KEY (objectid)'
            PostgresHelper.db_sql(host, db, db_user, port, pw, sql_query)
            
            # Im Moment wird dies nicht umgesetzt, da die lyr-Files nie auf die PostgreSQL zeigen
            # Falls eine Feature Class im Vek1 noch nicht existiert, wird sie kopiert um ein unnötiges
            # Umhängen der Begleitdaten im Anschluss an die Wippe zu verhindern
#              table_sp = table.split('.')
#              sql_query = "SELECT 1 FROM information_schema.tables WHERE table_schema = '" + table_sp[0] + "' AND table_name = '" + table_sp[1] + "'"
#              result_vek1 = PostgresHelper.db_sql(host, db, db_user, port, pw, sql_query)
#              if not result_vek1:
#                  self.logger.info("Ebene existiert noch nicht in vek1 und wird deshalb kopiert.")
#                  arcpy.Copy_management(source, target2)
#                  arcpy.ChangePrivileges_management(target2, rolle, "GRANT")
            
            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            count_source = int(arcpy.GetCount_management(source)[0])
              
            self.logger.info("Anzahl Objekte in Quell-Ebene: " + unicode(count_source))
            sql_query = 'SELECT COUNT(*) FROM ' + table
            count_target = PostgresHelper.db_sql(host, db, db_user, port, pw, sql_query, True)
            self.logger.info("Anzahl Objekte in Ziel-Ebene: " + unicode(count_target))
               
            if count_source != int(count_target):
                self.logger.error("Anzahl Objekte in Quelle und Ziel unterschiedlich!")
                raise Exception
            else:
                self.logger.info("Anzahl Objekte in Quelle und Ziel identisch!")
                   
            self.logger.info("Ebene " + ebename + " wurde kopiert")
            
        self.logger.info("Alle Ebenen wurden kopiert.")       
        self.finish()