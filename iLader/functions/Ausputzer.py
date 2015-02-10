# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class Ausputzer(TemplateFunction):
    '''
    Diese Funktion führt am Ende eines Imports/Tasks bestimmte
    Aufräumarbeiten aus:
    - Connection-Files löschen
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"Ausputzer"
        TemplateFunction.__init__(self, logger, task_config)
        
        # Der Abschnitt kann wahrscheinlich entfallen, da die Funktion
        # immer ausgeführt wird.
        # if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
        #     self.logger.info(u"Funktion " + self.name + u" wird ausgelassen.")
        # else:
        #     self.logger.info(u"Funktion " + self.name + u" wird ausgeführt.")
        #     self.start()
        
        self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        
        self.logger.info(u"Die Funktion " + self.name + u" arbeitet vor sich hin")
        
       
        self.finish()