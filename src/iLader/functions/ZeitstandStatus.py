# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class ZeitstandStatus(TemplateFunction):
    '''
    Diese Funktion setzt den Zeitstands-Status in der Tabelle ``TB_GEOPRODUKT_ZEISTAND``
    auf ``freigegeben`` (=9).
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "ZeitstandStatus"
        TemplateFunction.__init__(self, task_config, general_config)
        
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
        sql = "UPDATE %s.TB_GEOPRODUKT_ZEITSTAND SET STA_OBJECTID=9 WHERE GZS_OBJECTID=%s" % (self.general_config['connections']['TEAM_GEODB_DD_ORA'].username, self.task_config['gzs_objectid'])
        self.logger.info("SQL-Update wird ausgeführt: " + sql)
        self.general_config['connections']['TEAM_GEODB_DD_ORA'].db_write(sql)
        
        self.finish()