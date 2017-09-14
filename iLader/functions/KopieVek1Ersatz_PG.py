# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os
from iLader.helpers import PostgresHelper
from iLader.helpers import FME_helper

class KopieVek1Ersatz_PG(TemplateFunction):
    '''
    Kopiert saemtliche Vektorebenen aus der Instanz TEAM in die Instanz vek1 (PostgreSQL). Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz vek1 sind die Ebenen bereits vorhanden. Da keine Datenmodellaenderungen vorkommen kann, wird vor dem INSERT ein TRUNCATE ausgefuehrt (FME). 
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["vektor_ebenen"]``
    
    Der raeumlichen Indexes kann ebenfalls aufgrund der Locks nicht neu berechnet werden.
    '''
    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "KopieVek1Ersatz_PG"
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
        db = self.task_config['db_vek1_pg']
        port = self.task_config['port_pg']
        host = self.task_config['instances']['oereb']
        db_user = 'geodb'
        schema = self.task_config['schema']['geodb']
        pw = self.task_config['users']['geodb']
        source_sde = self.task_config['connections']['sde_conn_norm']
        fme_script = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + "\\helpers\\" + "EsriGeodatabase2PostGIS.fmw"
        
        # Jede Ebene durchgehen
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']       
            source_table = source.rsplit('\\',1)[1]
            table = ebene['ziel_vek1'].lower().rsplit('\\',1)[1]
            ebename = ebene['gpr_ebe'].lower()
            
            self.logger.info("Ebene " + ebename + " wird nach vek1 kopiert.")
            self.logger.info("Quelle: " + source)
            self.logger.info("Ziel: " + host + "/" + db +" "+ table)
            
            # Pruefen ob es die source Tabelle gibt
            if not arcpy.Exists(source):
                # Existiert die Quell-Ebene nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Quell-Ebene " + source + " existiert nicht!")
                raise Exception
        
            # Pruefen ob es die target Tabelle gibt
            table_sp = table.split('.')
            sql_query = "SELECT 1 FROM information_schema.tables WHERE table_schema = '" + table_sp[0] + "' AND table_name = '" + table_sp[1] + "'"
            result_vek1 = PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query, True)
            if result_vek1 is None:
                # Gibt es die Ziel-Ebene noch nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Ziel-Ebene " + table + " existiert nicht!")
                raise Exception
            
            # Daten kopieren
            # Copy-Script, Table Handling auf Truncate umstellen, damit Tabelle nicht gelöscht wird
            self.logger.info("Ebene " + host + "/" + db +" "+ table + " wird geleert (Truncate) und aufgefuellt (Insert).")
            fme_logfile = FME_helper.prepare_fme_log(fme_script, (self.task_config['log_file']).rsplit('\\',1)[0])
            # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
            # Daher muessen workspace und parameters umgewandelt werden!
            parameters = {
                'TABELLEN': str(source_table),
                'POSTGIS_DB': str(db),
                'POSTGIS_HOST': str(host),
                'POSTGIS_PORT': str(port),
                'POSTGIS_USER': str(db_user),
                'SCHEMA_NAME': str(schema),
                'POSTGIS_PASSWORD': str(pw),
                'LOGFILE': str(fme_logfile),
                'INPUT_SDE': str(source_sde),
                'TABLE_HANDLING': "TRUNCATE_EXISTING" 
            }
            # FME-Skript starten
            FME_helper.fme_runner(self, str(fme_script), parameters)
            
            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            count_source = int(arcpy.GetCount_management(source)[0])
              
            self.logger.info("Anzahl Objekte in Quell-Ebene: " + unicode(count_source))
            sql_query = 'SELECT COUNT(*) FROM ' + table
            count_target = PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query, True)
            self.logger.info("Anzahl Objekte in Ziel-Ebene: " + unicode(count_target))
               
            if count_source != int(count_target):
                self.logger.error("Anzahl Objekte in Quelle und Ziel unterschiedlich!")
                raise Exception
            else:
                self.logger.info("Anzahl Objekte in Quelle und Ziel identisch!")
            
            self.logger.info("Ebene " + ebename + " wurde ersetzt")
        
        self.logger.info("Alle Ebenen wurden ersetzt.")       
        self.finish()