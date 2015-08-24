# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class ImportArchiv(TemplateFunction):
    '''
    Diese Funktion kopiert sowohl das Logfile als auch das task_config-File auf dem Arbeitsshare.
    Allfällige Aufräumarbeiten können auch in dieser Funktion vorgenommen werden.
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "ImportArchiv"
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