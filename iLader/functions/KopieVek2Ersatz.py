# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy

class KopieVek2Ersatz(TemplateFunction):
    '''
    Kopiert sämtliche Vektorebenen aus der Instanz TEAM in die Instanz VEK2. Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz VEK2 sind die Ebenen bereits vorhanden und müssen vorgängig
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
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "KopieVek2Ersatz"
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
        rolle = self.task_config['rolle']
        
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']
            target = ebene['ziel_vek2']
            ebename = ebene['gpr_ebe']
            self.logger.info("Ebene " + ebename + " wird nach VEK2 kopiert.")
            self.logger.info("Quelle: " + source)
            self.logger.info("Ziel: " + target)
            if not arcpy.Exists(source):
                # Existiert die Quell-Ebene nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Quell-Ebene " + source + " existiert nicht!")
                raise Exception
            if arcpy.Exists(target):
                # Gibt es die Ziel-Ebene bereits, muss sie gelöscht werden
                self.logger.info("Ebene " + target + " wird nun gelöscht!")
                arcpy.Delete_management(target)
            arcpy.Copy_management(source, target)
            # Berechtigungen setzen
            self.logger.info("Berechtigungen für Ebene " + target + " werden gesetzt: Rolle " + rolle)
            arcpy.ChangePrivileges_management(target, rolle, "GRANT")
            
            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            count_source = int(arcpy.GetCount_management(source)[0])
            self.logger.info("Anzahl Objekte in Quell-Ebene: " + unicode(count_source))
            count_target = int(arcpy.GetCount_management(target)[0])
            self.logger.info("Anzahl Objekte in Ziel-Ebene: " + unicode(count_target))
            
            if count_source != count_target:
                self.logger.error("Anzahl Objekte in Quelle und Ziel unterschiedlich!")
                raise Exception
            else:
                self.logger.info("Anzahl Objekte in Quelle und Ziel identisch!")
                
            self.logger.info("Ebene " + ebename + " wurde kopiert")    
            
        self.logger.info("Alle Ebenen wurden kopiert.")       
        self.finish()