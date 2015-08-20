# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import cx_Oracle

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
        self.name = "ZeitstandAngelegt"
        TemplateFunction.__init__(self, logger, task_config)
        
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
        
        sql = "UPDATE " + schema + ".TB_GEOPRODUKT_ZEITSTAND SET STA_OBJECTID=1 WHERE GZS_OBJECTID=" + gzs_objectid
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
            self.logger.error("Status 'angelegt' konnte nicht gesetzt werden.")
            del cursor
            del connection
            raise Exception       
        self.finish()