# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os
import cx_Oracle

class TransferVek1(TemplateFunction):
    '''
    Kopiert die ÖREBK-Transferstruktur nach Vek1. Es werden nur diejenigen Teile der
    Transferstruktur kopiert, die zum importierten Geoprodukt gehören.
    Wenn zu diesem Geoprodukt keine ÖREBK-Tickets gefunden wurden, wird die ÖREBK-
    Transferstruktur gar nicht kopiert.
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "TransferVek1"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("ÖREBK-Transferstruktur wird nach VEK1 kopiert.")
        source_connection = self.task_config['connections']['sde_conn_team_oereb']
        target_connection = self.task_config['connections']['sde_conn_vek1_oereb"']
        oereb_tables = self.task_config['oereb']['tabellen']
        liefereinheiten = self.task_config['oereb']['liefereinheiten']
        
        if liefereinheiten == '':
            self.logger.info('Für diesen Import konnten keine ÖREBK-Liefereinheiten ermittelt werden.')
            self.logger.info('Die ÖREBK-Transferstruktur wird daher nicht importiert.')
        else:
            for oereb_table in oereb_tables:
                oereb_tablename = oereb_table['tablename']
                oereb_table_filter_field = oereb_table['filter_field']
                username = self.task_config['schema']['oereb']
                password = self.task_config['users']['oereb']
                db = self.task_config['instances']['vek1']
                
                oereb_delete_sql = "DELETE FROM %s WHERE %s IN %s" % (oereb_tablename, oereb_table_filter_field, liefereinheiten)
                self.logger.info("Deleting...")
                self.logger.info(oereb_delete_sql)
                vek1_connection_string = username + "/" + password + "@" + db
                # Mit dem With-Statement wird sowohl committed als auch die
                # Connection- und Cursor-Objekte automatisch geschlossen
                with cx_Oracle.connect(vek1_connection_string) as conn:
                    cur = conn.cursor()
                    cur.execute(oereb_delete_sql)
                
                source = os.path.join(source_connection, username + "." + oereb_tablename)
                source_layer = oereb_tablename + "_source_layer"
                target = os.path.join(target_connection, username + "." + oereb_tablename)
                target_layer = oereb_tablename + "_target_layer"
                where_clause = oereb_table_filter_field + " IN " + liefereinheiten
                self.logger.info("WHERE-Clause: " + where_clause)
                if arcpy.Describe(source).datasetType=='Table':
                    # MakeTableView funktioniert nicht, da mangels OID-Feld keine Selektionen gemacht werden können
                    # MakeQueryTable funktioniert, da hier ein virtuelles OID-Feld erstellt wird. Im Gegenzug wird die
                    # Tabelle temporär zwischengespeichert.
                    arcpy.MakeQueryTable_management(source, source_layer, 'ADD_VIRTUAL_KEY_FIELD', '#', '#',  where_clause)
                else:
                    arcpy.MakeFeatureLayer_management(source, source_layer, where_clause)
                    
                self.logger.info("Appending...")
                arcpy.Append_management(source_layer, target, "TEST")
                # Die QueryTables/FeatureLayers müssen nach dem Append gemacht werden,
                # da der QueryTable nicht mehr live auf die Daten zugreift, sondern
                # auf der Festplatte zwischengespeichert ist.
                if arcpy.Describe(source).datasetType=='Table':
                    arcpy.MakeQueryTable_management(target, target_layer, 'ADD_VIRTUAL_KEY_FIELD', '#', '#',  where_clause)
                else:
                    arcpy.MakeFeatureLayer_management(target, target_layer, where_clause)
                    
                self.logger.info("Counting..")
                source_count = int(arcpy.GetCount_management(source_layer)[0])
                self.logger.info("Anzahl Features im Quell-Layer: " + unicode(source_count))
                target_count = int(arcpy.GetCount_management(target_layer)[0])
                self.logger.info("Anzahl Features im Ziel-Layer: " + unicode(target_count))
                if source_count!=target_count:
                    self.logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
                    raise Exception
                
                self.logger.info("Die Tabelle " + oereb_tablename + " wurde kopiert.")
                        
            self.logger.info("Die ÖREBK-Transferstruktur wurde kopiert.")       
            self.finish()