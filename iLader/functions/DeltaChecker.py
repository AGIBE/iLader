# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class DeltaChecker(TemplateFunction):
    '''
    Bei dieser Funktion handelt es sich nur um den Aufruf eines bereits
    bestehenden Tools und die Weiterverarbeitung des Rückgabewertes dieses
    Tools.
    Die Funktion ruft den DeltaChecker anhand der Informationen aus der
    task_config auf, übernimmt den Rückgabewert des DeltaCheckers und
    verarbeitet ihn wiefolgt weiter:
    
    - Der Rückgabewert der Funktion ist ``TRUE``, wenn der Rückgabewert
      des DeltaCheckers ``keine DMA`` ist.
    - Der Rückgabewert der Funktion ist ``TRUE``, wenn der Rückgabewert
      des DeltaCheckers ``DMA`` ist und ``task_config["qs"]["dma_erlaubt"]=TRUE``
    - Der Rückgabewert der Funktion ist ``FALSE``, wenn der Rückgabewert
      des DeltaCheckers ``DMA`` ist und ``task_config["qs"]["dma_erlaubt"]=FALSE``
      
    Der Rückgabewert wird in ``task_config["qs"]["deltachecker_passed"]``
    festgehalten.
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "DeltaChecker"
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
        
        self.logger.info("Die Funktion " + self.name + " arbeitet vor sich hin")
        
       
        self.finish()