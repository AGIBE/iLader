# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class GeoDBProzess(TemplateFunction):
    '''
    Die Funktion trägt die Task-Id in die GeoDBProzess (Tabelle GEOPRODUKTE.TASK_ID) ein.
    '''
    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "GeoDBProzess"
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
        gdbp_sql = "UPDATE %s.GEOPRODUKTE SET TASK_ID=%s WHERE CODE='%s'" % (self.task_config['schema']['gdbp'], self.task_config['task_id'], self.task_config['gpr'])
        self.logger.info("SQL-Update wird ausgeführt: ")
        self.logger.info(gdbp_sql)
        self.general_config['connections'][['TEAM_GEODB_DD_ORA']].db_write(gdbp_sql)
        
        self.finish()