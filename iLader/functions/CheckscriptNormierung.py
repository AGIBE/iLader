# -*- coding: utf-8 -*-
'''
Created on 09.01.2015

@author: Peter Schär
'''
from .TemplateFunction import TemplateFunction

class CheckscriptNormierung(TemplateFunction):
    '''
    Führt das Checkscript Normierung aus
    '''
    
    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"CheckscriptNormierung"
        TemplateFunction.__init__(self, logger, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info(u"Funktion " + self.name + u" wird ausgelassen.")
        else:
            self.logger.info(u"Funktion " + self.name + u" wird ausgeführt.")
            self.__execute()
            
        
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        
        self.logger.info(u"Die Funktion " + self.name + u" arbeitet vor sich hin")
        
        
        self.finish()