# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os
from iLader.helpers import PostgresHelper, FME_helper, DummyHandler

class KopieVek2Neu_PG(TemplateFunction):
    '''
    Kopiert sämtliche Vektorebenen aus der Instanz TEAM in die Instanz vek2 (PostgreSQL). Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz vek2 sind die Ebenen nicht vorhanden. Da aber z.B. aufgrund eines
    abgebrochenen Imports durchaus verwaiste Ebenen vorhanden sein kännen, muss diese 
    Funktion vorgängig prüfen, ob die Ebenen schon existieren und sie gegebenenfalls
    löschen.
    
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
        self.name = "KopieVek2Neu_PG"
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
        fme_script = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + "\\helpers\\" + "EsriGeodatabase2PostGIS.fmw"
        
        # Jede Ebene durchgehen
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']       
            source_table = source.rsplit('\\',1)[1]
            table = ebene['ziel_vek2'].rsplit('\\',1)[1]
            ebename = ebene['gpr_ebe'].lower()
            dummy_entry = False
            
            self.logger.info("Ebene " + ebename + " wird nach vek2 kopiert.")
            self.logger.info("Quelle: " + source)
            self.logger.info("Ziel: " + host + "/" + db +" "+ table)
            
            # Pruefen ob es die source Tabelle gibt
            if not arcpy.Exists(source):
                # Existiert die Quell-Ebene nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Quell-Ebene " + source + " existiert nicht!")
                raise Exception
                
            # Prüfen ob die source Tabelle leer ist
            count_source = int(arcpy.GetCount_management(source)[0])
            if count_source == 0:
                self.logger.warn("Quell-Ebene " + source + " ist leer. Es wird ein Dummy-Eintrag erstellt.")
                DummyHandler.create_dummy(source)
                dummy_entry = True
                
            # Daten kopieren
            # Copy-Script
            fme_logfile = FME_helper.prepare_fme_log(fme_script, (self.task_config['log_file']).rsplit('\\',1)[0])
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
            FME_helper.fme_runner(self, str(fme_script), parameters)
      
            # Dummy-Eintrag entfernen
            if dummy_entry:
                self.logger.info("Dummy-Eintrag wird wieder entfernt.")
                DummyHandler.delete_dummy(self, source, table, host, db, db_user, port, pw)
            
            # Berechtigungen setzen
            self.logger.info("Berechtigungen für Ebene " + table + " wird gesetzt: Rolle " + rolle)
            sql_query = 'GRANT SELECT ON ' + table + ' TO ' + rolle
            PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query)
               
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
                   
            self.logger.info("Ebene " + ebename + " wurde kopiert")
            
            
        self.logger.info("Alle Ebenen wurden kopiert.")        
       
        self.finish()