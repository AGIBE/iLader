# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
from iLader.helpers import OracleHelper

class ZeitstandStatus(TemplateFunction):
    '''
    Diese Funktion setzt den Zeitstands-Status in der Tabelle ``TB_GEOPRODUKT_ZEISTAND``
    auf ``freigegeben`` (=9).
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "ZeitstandStatus"
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
        db = self.task_config['instances']['team']
        schema = self.task_config['schema']['geodb_dd']
        username = 'geodb_dd'
        password = self.task_config['users'][username]
        gzs_objectid = self.task_config['gzs_objectid']
        
        sql = "UPDATE " + schema + ".TB_GEOPRODUKT_ZEITSTAND SET STA_OBJECTID=9 WHERE GZS_OBJECTID=" + gzs_objectid
        self.logger.info("SQL-Update wird ausgeführt: " + sql)
        
        OracleHelper.writeOracleSQL_check(self, db, username, password, sql, "Status 'angelegt' konnte nicht gesetzt werden.")
        
        self.finish()