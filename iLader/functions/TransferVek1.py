# -*- coding: utf-8 -*-
'''
Created on 14.01.2015

@author: Peter Schär
'''
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

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
        
        self.logger.info(u"Die Funktion " + self.name + u" arbeitet vor sich hin")
        
       
        self.finish()