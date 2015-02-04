# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os

class TransferVek1(TemplateFunction):
    '''
    Kopiert die Transferstruktur nach Vek1, bestehende Objekt werden ersetzt.
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"TransferVek1"
        TemplateFunction.__init__(self, logger, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info(u"Funktion " + self.name + u" wird ausgelassen.")
        else:
            self.logger.info(u"Funktion " + self.name + u" wird ausgeführt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("ÖREBK-Transferstruktur wird nach VEK1 kopiert.")
        source_connection = self.task_config['connections']['sde_conn_team_oereb']
        target_connection = self.task_config['connections']['sde_conn_vek1_oereb"']
        
        for tabelle in self.task_config['oereb_tabellen']:
            source = os.path.join(source_connection, tabelle)
            target = os.path.join(target_connection, tabelle) 
            self.logger.info("Tabelle " + tabelle + " wird nach VEK1 kopiert.")
            self.logger.info("Quelle: " + source)
            self.logger.info("Ziel: " + target)
            if not arcpy.Exists(source):
                # Existiert die Quell-Ebene nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Quell-Ebene " + source + " existiert nicht!")
                raise Exception
            if not arcpy.Exists(target):
                # Gibt es die Ziel-Ebene noch nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Ziel-Ebene " + target + " existiert nicht!")
                raise Exception
            
            self.logger.info("Tabelle " + target + " wird geleert (Truncate).")
            arcpy.TruncateTable_management(target)
            
            self.logger.info("Tabelle " + target + " wird aufgefüllt mit Tabelle " + source)
            # APPEND wird mit dem Parameter TEST ausgeführt. Allfällige (eigentlich nicht
            # erlaubte) Datenmodelländerungen würden so doch noch bemerkt.
            arcpy.Append_management(source, target, "TEST")
            
            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            count_source = int(arcpy.GetCount_management(source))
            self.logger.info("Anzahl Objekte in Quell-Ebene: " + str(count_source))
            count_target = int(arcpy.GetCount_management(target))
            self.logger.info("Anzahl Objekte in Ziel-Ebene: " + str(count_target))
            
            if count_source != count_target:
                self.logger.warn("Anzahl Objekte in Quelle und Ziel unterschiedlich!")
                #TODO: definieren, ob in diesem Fall das Script abbrechen soll
            else:
                self.logger.info("Anzahl Objekte in Quelle und Ziel identisch!")
            
            self.logger.info("Tabelle " + tabelle + " wurde ersetzt")
        
        self.logger.info("Alle ÖREBK-Tabellen wurden ersetzt.")
               
        self.finish()