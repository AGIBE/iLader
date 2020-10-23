# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class ZeitstandAngelegt(TemplateFunction):
    '''
    Diese Funktion erfasst den Status angelegt (Wert=1) in der Tabelle ``tb_geoprodukt_zeitstand``,
    wenn es sich beim Usecase um eine Korrektur eines Geoproduktzeitstandes handelt. In allen anderen
    Usecases wird dieser Wert durch die Synchronisation GeoDBmeta => DataDictionary gesetzt.
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "ZeitstandAngelegt"
        TemplateFunction.__init__(self, task_config, general_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['resume']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        sql = "UPDATE %s.TB_GEOPRODUKT_ZEITSTAND SET STA_OBJECTID=1 WHERE GZS_OBJECTID=%s" % (self.general_config['connections']['TEAM_GEODB_DD_ORA'].username, self.task_config['gzs_objectid'])
        self.logger.info("SQL-Update wird ausgeführt: " + sql)
        self.general_config['connections']['TEAM_GEODB_DD_ORA'].db_write(sql)
           
        self.finish()