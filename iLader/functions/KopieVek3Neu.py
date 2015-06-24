# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy

class KopieVek3Neu(TemplateFunction):
    '''
    Kopiert sämtliche Vektorebenen aus der Instanz TEAM in die Instanz VEK3. Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz VEK3 sind die Ebenen nicht vorhanden. Da aber z.B. aufgrund eines
    abgebrochenen Imports durchaus verwaiste Ebenen vorhanden sein können, muss diese 
    Funktion vorgängig prüfen, ob die Ebenen schon existieren und sie gegebenenfalls
    löschen.
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["vektor_ebenen"]``
    
    Nach dem Kopiervorgang setzt die Funktion auch noch die korrekten Berechtigungen d.h.
    sie vergibt SELECT-Rechte an eine Rolle. Die Rolle ist in task_config abgelegt:
    
    - ``task_config["rolle"]``
    
    Auf das explizite Berechnen des räumlichen Indexes wird verzichtet.
    '''
    #TODO: Precision etc.
    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"KopieVek3Neu"
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
        rolle = self.task_config['rolle']
        
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']
            target = ebene['ziel_vek3']
            ebename = ebene['gpr_ebe']
            self.logger.info("Ebene " + ebename + " wird nach VEK3 kopiert.")
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
            # Berechtigungen setzen
            self.logger.info("Berechtigungen für Ebene " + target + " werden gesetzt: Rolle " + rolle)
            arcpy.ChangePrivileges_management(target, rolle, "GRANT")
            
            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            count_source = int(arcpy.GetCount_management(source)[0])
            self.logger.info("Anzahl Objekte in Quell-Ebene: " + str(count_source))
            count_target = int(arcpy.GetCount_management(target)[0])
            self.logger.info("Anzahl Objekte in Ziel-Ebene: " + str(count_target))
            
            if count_source != count_target:
                self.logger.warn("Anzahl Objekte in Quelle und Ziel unterschiedlich!")
                #TODO: definieren, ob in diesem Fall das Script abbrechen soll
            else:
                self.logger.info("Anzahl Objekte in Quelle und Ziel identisch!")
            
            self.logger.info("Ebene " + ebename + " wurde kopiert")
        
        self.logger.info("Alle Ebenen wurden kopiert.")
       
        self.finish()