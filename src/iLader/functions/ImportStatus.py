# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import time

class ImportStatus(TemplateFunction):
    '''
    Diese Funktion passt den Status in der Tabelle ``TB_IMPORTE_GEODB`` an. Folgende Felder
    werden geändert:
    
    - ``imp_status`` erhält den Wert ``importiert`` (=5)
    - ``imd_datum_ende`` erhält den aktuellen Zeitstempel
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "ImportStatus"
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
        today = time.strftime("%d.%m.%y")
        importstatus_sql = "UPDATE %s.TB_TASK SET TASK_STATUS=5, TASK_ENDE=TO_DATE('%s', 'DD.MM.YY') WHERE TASK_OBJECTID=%s" % (self.task_config['schema']['geodb_dd'], today, self.task_config['task_id'])
        self.logger.info("SQL-Update wird ausgeführt: " + importstatus_sql)
        self.general_config['connections'][['TEAM_GEODB_DD_ORA']].db_write(importstatus_sql)

        self.finish()