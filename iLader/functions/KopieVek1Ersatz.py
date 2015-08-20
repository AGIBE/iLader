# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy

class KopieVek1Ersatz(TemplateFunction):
    '''
    Kopiert sämtliche Vektorebenen aus der Instanz TEAM in die Instanz VEK1. Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz VEK2 sind die Ebenen bereits vorhanden. Sie können nicht gelöscht werden,
    da sie gelockt sind. Deshalb müssen sie geleert (Truncate) und gefüllt (Append) werden. 
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["vektor_ebenen"]``
    
    Der räumlichen Indexes kann ebenfalls aufgrund der Locks nicht neu berechnet werden.
    '''
    #TODO: Precision etc.
    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"KopieVek1Ersatz"
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
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']
            target = ebene['"ziel_vek1']
            ebename = ebene['gpr_ebe']
            self.logger.info("Ebene " + ebename + " wird nach VEK1 kopiert.")
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
            
            self.logger.info("Ebene " + target + " wird geleert (Truncate).")
            arcpy.TruncateTable_management(target)
            
            self.logger.info("Ebene " + target + " wird aufgefüllt mit Ebene " + source)
            # APPEND wird mit dem Parameter TEST ausgeführt. Allfällige (eigentlich nicht
            # erlaubte) Datenmodelländerungen würden so doch noch bemerkt.
            arcpy.Append_management(source, target, "TEST")
            
            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            count_source = int(arcpy.GetCount_management(source)[0])
            self.logger.info("Anzahl Objekte in Quell-Ebene: " + unicode(count_source))
            count_target = int(arcpy.GetCount_management(target)[0])
            self.logger.info("Anzahl Objekte in Ziel-Ebene: " + unicode(count_target))
            
            if count_source != count_target:
                self.logger.warn("Anzahl Objekte in Quelle und Ziel unterschiedlich!")
                #TODO: definieren, ob in diesem Fall das Script abbrechen soll
            else:
                self.logger.info("Anzahl Objekte in Quelle und Ziel identisch!")
            
            self.logger.info("Ebene " + ebename + " wurde ersetzt")
        
        self.logger.info("Alle Ebenen wurden ersetzt.")       
        self.finish()