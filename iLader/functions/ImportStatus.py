# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import cx_Oracle
import time

class ImportStatus(TemplateFunction):
    '''
    Diese Funktion passt den Status in der Tabelle ``TB_IMPORTE_GEODB`` an. Folgende Felder
    werden geändert:
    
    - ``imp_status`` erhält den Wert ``importiert`` (=5)
    - ``imd_datum_ende`` erhält den aktuellen Zeitstempel
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"ImportStatus"
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
        db = self.task_config['instances']['team']
        schema = self.task_config['schema']['geodb_dd']
        username = 'geodb_dd'
        password = self.task_config['users'][username]
        task_id = self.task_config['task_id']
        today = time.strftime("%d.%m.%y")
        
        sql = "UPDATE " + schema + ".TB_TASK SET TASK_STATUS=5, TASK_ENDE=TO_DATE('" + today + "', 'DD.MM.YY') WHERE TASK_OBJECTID=" + task_id
        self.logger.info("SQL-Update wird ausgeführt: " + sql)
        
        connection = cx_Oracle.connect(username, password, db)  
        cursor = connection.cursor()
        cursor.execute(sql)
        if cursor.rowcount == 1:
            # Nur wenn genau 1 Zeile aktualisiert wurde, ist alles i.O. 
            self.logger.info("Query wurde ausgeführt!")
            connection.commit()
            del cursor
            del connection
        else:
            # Wenn nicht genau 1 Zeile aktualisiert wurde, muss abgebrochen werden
            self.logger.error("Query wurde nicht erfolgreich ausgeführt.")
            self.logger.error("Status konnte nicht gesetzt werden.")
            del cursor
            del connection
            raise Exception          

        self.finish()