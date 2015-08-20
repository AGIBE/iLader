# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy

class KopieRas1Neu(TemplateFunction):
    '''
    Kopiert sämtliche Rasterebenen (ganzflächig aktualisiert) aus der Instanz TEAM in die Instanz RAS1.
    Die Daten werden einmal als aktueller und als historischer Zeitstand abgelegt. Folgende Typen werden kopiert:
    
    - Raster Datasets
    
    In der Zielinstanz RAS1 sind die Ebenen nicht vorhanden. Da aber z.B. aufgrund eines
    abgebrochenen Imports durchaus verwaiste Ebenen vorhanden sein können, muss diese 
    Funktion vorgängig prüfen, ob die Ebenen schon existieren und sie gegebenenfalls
    löschen.
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["raster_ebenen"]``
    
    Nach dem Kopiervorgang setzt die Funktion auch noch die korrekten Berechtigungen d.h.
    sie vergibt SELECT-Rechte an eine Rolle. Die Rolle ist in task_config abgelegt:
    
    - ``task_config["rolle"]``

    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "KopieRas1Ne"
        TemplateFunction.__init__(self, logger, task_config)
        
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
        rolle = self.task_config['rolle']
        
        for ebene in self.task_config['raster_ebenen']:
            source = ebene['quelle']
            target = ebene['ziel_ras1']
            target_zs = ebene['ziel_ras1_zs']
            ebename = ebene['gpr_ebe']
            self.logger.info("Ebene " + ebename + " wird nach RAS1 kopiert.")
            self.logger.info("Quelle: " + source)
            self.logger.info("Ziel: " + target)
            if not arcpy.Exists(source):
                # Existiert die Quell-Ebene nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Quell-Ebene " + source + " existiert nicht!")
                raise Exception
            if arcpy.Exists(target):
                # Gibt es die Ziel-Ebene bereits, muss sie gelöscht werden
                self.logger.warn("Ebene " + target + " gibt es bereits. Sie wird nun gelöscht!")
                arcpy.Delete_management(target)
            arcpy.Copy_management(source, target)            
            self.logger.info("Ziel Zeitstand: " + target_zs)
            if arcpy.Exists(target_zs):
                # Gibt es die Ziel-Ebene bereits, muss sie gelöscht werden
                self.logger.warn("Ebene " + target_zs + " gibt es bereits. Sie wird nun gelöscht!")
                arcpy.Delete_management(target_zs)
            arcpy.Copy_management(source, target_zs)
            # Berechtigungen setzen
            self.logger.info("Berechtigungen für Ebene " + target + " werden gesetzt: Rolle " + rolle)
            arcpy.ChangePrivileges_management(target, rolle, "GRANT")
            self.logger.info("Berechtigungen für Ebene " + target_zs + " werden gesetzt: Rolle " + rolle)
            arcpy.ChangePrivileges_management(target_zs, rolle, "GRANT")
            
            self.logger.info("Ebene " + ebename + " wurde kopiert")    
            
        self.logger.info("Alle Ebenen wurden kopiert.")        
       
        self.finish()