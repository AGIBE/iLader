# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
from iLader.helpers import OracleHelper

class GeoDBProzess(TemplateFunction):
    '''
    Die Funktion trägt die Task-Id in die GeoDBProzess (Tabelle GEOPRODUKTE.TASK_ID) ein.
    '''
    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "GeoDBProzess"
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
        db = self.task_config['instances']['work']
        schema = self.task_config['schema']['gdbp']
        username = 'gdbp'
        password = self.task_config['users'][username]
        
        task_id = self.task_config['task_id']
        gpr_code = self.task_config['gpr']
        
        sql = "UPDATE " + schema + ".GEOPRODUKTE SET TASK_ID=" + unicode(task_id) + " WHERE CODE='" + gpr_code + "'"
        self.logger.info("SQL-Update wird ausgeführt: " + sql)
        
        OracleHelper.writeOracleSQL_check(self, db, username, password, sql, "Query hat keinen oder mehr als einen Record aktualisiert!", excep=False)
        
        self.finish()