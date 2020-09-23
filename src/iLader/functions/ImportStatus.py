# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
from iLader.helpers import OracleHelper
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
        db = self.task_config['instances']['team']
        schema = self.task_config['schema']['geodb_dd']
        username = 'geodb_dd'
        password = self.task_config['users'][username]
        task_id = self.task_config['task_id']
        today = time.strftime("%d.%m.%y")
        
        sql = "UPDATE " + schema + ".TB_TASK SET TASK_STATUS=5, TASK_ENDE=TO_DATE('" + today + "', 'DD.MM.YY') WHERE TASK_OBJECTID=" + unicode(task_id)
        self.logger.info("SQL-Update wird ausgeführt: " + sql)
        
        OracleHelper.writeOracleSQL_check(self, db, username, password, sql, "Status konnte nicht gesetzt werden.")

        self.finish()