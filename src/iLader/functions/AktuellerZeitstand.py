# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class AktuellerZeitstand(TemplateFunction):
    '''
    Diese Funktion trägt die ``gzs_objectid`` des importierten Geoprodukt-Zeitstandes
    in die Tabelle ``tb_geoprodukt`` ein.
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "AktuellerZeitstand"
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
        gzs_objectid_sql = "UPDATE %s.TB_GEOPRODUKT SET GZS_OBJECTID=%s WHERE GPR_BEZEICHNUNG='%s'" % (self.task_config['schema']['geodb_dd'], self.task_config['gzs_objectid'], self.task_config['gpr'])
        self.logger.info("SQL-Update wird ausgeführt:")
        self.logger.info(gzs_objectid_sql)
        self.general_config['connections'][['TEAM_GEODB_DD_ORA']].db_write(gzs_objectid_sql)
       
        self.finish()