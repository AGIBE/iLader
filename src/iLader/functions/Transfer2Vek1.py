# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os

class Transfer2Vek1(TemplateFunction):
    '''
    Kopiert die ÖREBK-Transferstruktur (OEREB2) nach Vek1. Es werden nur diejenigen Teile der
    Transferstruktur kopiert, die zum importierten Geoprodukt gehören.
    Wenn zu diesem Geoprodukt keine ÖREBK-Tickets gefunden wurden, wird die ÖREBK-
    Transferstruktur gar nicht kopiert.
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Transfer2Vek1"
        TemplateFunction.__init__(self, task_config, general_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['resume']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("ÖREBK-Transferstruktur (OEREB2) wird nach VEK1 kopiert.")
        source_connection = self.general_config['connection_files']['TEAM_OEREB2_ORA']
        target_connection = self.general_config['connection_files']['VEK1_OEREB2_ORA']
        oereb_tables = self.task_config['oereb']['tabellen_ora']
        liefereinheiten = self.task_config['oereb']['liefereinheiten']
        
        if liefereinheiten == '()':
            self.logger.info('Für diesen Import konnten keine ÖREBK-Liefereinheiten ermittelt werden.')
            self.logger.info('Die ÖREBK-Transferstruktur wird daher nicht importiert.')
        else:
            for oereb_table in oereb_tables:
                oereb_tablename = oereb_table['tablename']
                oereb_table_filter_field = oereb_table['filter_field']
                
                oereb_delete_sql = "DELETE FROM %s WHERE %s IN %s" % (oereb_tablename, oereb_table_filter_field, liefereinheiten)
                self.logger.info("Deleting...")
                self.logger.info(oereb_delete_sql)
                
                self.general_config['connection']['VEK1_OEREB2_ORA'].db_write(oereb_delete_sql)
                
                username = self.general_config['connection']['VEK1_OEREB2_ORA'].username
                source = os.path.join(source_connection, username + "." + oereb_tablename)
                source_layer = oereb_tablename + "_source_layer_vek1_2"
                target = os.path.join(target_connection, username + "." + oereb_tablename)
                target_layer = oereb_tablename + "_target_layer_vek1_2"
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
                        
            self.logger.info("Die ÖREBK-Transferstruktur (OEREB2) wurde kopiert.")       
            self.finish()