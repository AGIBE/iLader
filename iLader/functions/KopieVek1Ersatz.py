# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

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
        
        self.logger.info(u"Die Funktion " + self.name + u" arbeitet vor sich hin")
        
       
        self.finish()