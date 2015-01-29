# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class ZeitstandAngelegt(TemplateFunction):
    '''
    Diese Funktion erfasst den Status angelegt (Wert=1) in der Tabelle ``tb_geoprodukt_zeitstand``,
    wenn es sich beim Usecase um eine Korrektur eines Geoproduktzeitstandes handelt. In allen anderen
    Usecases wird dieser Wert durch die Synchronisation GeoDBmeta => DataDictionary gesetzt.
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"ZeitstandAngelegt"
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