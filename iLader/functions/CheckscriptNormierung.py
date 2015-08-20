# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class CheckscriptNormierung(TemplateFunction):
    '''
    Das Checkscript Normierung wird ausgeführt. Der Rückgabewert übernommen und in der
    task_config abgelegt. Bei dieser Funktion handelt es sich nur um den Aufruf eines bereits
    bestehenden Tools und die Weiterverarbeitung des Rückgabewertes dieses Tools.
    
    Diese Funktion ruft das Checkscript Normierung auf. Das Checkscript gibt einen Rückgabewert
    ``bestanden`` / ``nicht bestanden`` zurück. Dieser Rückgabewert wird in
    ``task_config["qs"]["checkscript_passed"]`` festgehalten (``TRUE`` oder ``FALSE``).
    '''
    
    def __init__(self, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "CheckscriptNormierung"
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