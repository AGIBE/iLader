# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class QSBenachrichtigung(TemplateFunction):
    '''
    Wenn ``task_config["qs"]["qs_gesamt_passed"]=FALSE`` d.h. die
    Qualitätssicherung wurde nicht erfolgreich durchlaufen, führt diese
    Funktion folgende Aktionen aus:
    
    - Benachrichtigungsmail versenden (Adressatenkreis t.b.d.)
    - Import abbrechen (raise exception, Error-Meldung im Log)

    Wenn ``task_config["qs"]["qs_gesamt_passed"]=TRUE`` d.h. die
    Qualitätssicherung wurde erfolgreich durchlaufen, führt diese
    Funktion keine weiteren Aktionen aus.
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "QSBenachrichtigung"
        TemplateFunction.__init__(self, logger, task_config)
        
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