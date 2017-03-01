# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import json
from iLader.helpers.Crypter import Crypter
import copy
import logging
import cx_Oracle

class TemplateFunction(object):
    '''
    Diese Klasse ist eine abstrakte Klasse, von der
    sämtliche Funktionen erben. Als abstrakte Klasse wird
    sie nie selber ausgeführt werden, sie dient nur als
    Vorlage und enthält Code, der von allen Funktionen
    geteilt wird.
    '''


    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.logger = logging.getLogger("iLaderLogger")
        self.task_config = task_config
        
    def write_task_config(self):
        '''
        schreibt die aktuelle task_config in ein JSON-File.
        '''
        f = open(self.task_config['task_config_file'], "w")
        # Alle Passwörter in der task_config müssen vor dem
        # Rausschreiben verschlüsselt werden. Damit sind sie
        # nur im Memory im Klartext vorhanden.
        # Deepcopy ist nötig, damit auch wirklich eine Kopie
        # des gesamten Dicts (inkl. aller verschachtelter
        # Objekte) gemacht wird.
        encrypted_task_config = copy.deepcopy(self.task_config)
        crypter = Crypter()
        for key, value in encrypted_task_config['users'].iteritems():
            encrypted_task_config['users'][key] = crypter.encrypt(value) 
                       
        json.dump(encrypted_task_config, f, indent=4)
        f.close()
        
    def get_old_statistics(self,connection):
        index_tables = []
        cursor = connection.cursor()
        #Prüfen ob veraltete Statistiken vorhanden sind
        index_tables_sql = "select table_name from DBA_TAB_STATISTICS where owner='GEODB' and table_name not like '%_IDX$%' and (stale_stats='YES' or stale_stats is null)" 
        cursor.execute(index_tables_sql)
        result_list = cursor.fetchall()
        for result in result_list:
            index_tables.append(result[0])
        cursor.close()
        return index_tables
    
    def get_indexes_of_table(self,indexed_table,connection):
        indexes = []
        cursor = connection.cursor()
        indexes_sql = "select index_name from DBA_INDEXES where table_name='" + indexed_table + "' and table_owner='GEODB' and index_type='NORMAL'" 
        cursor.execute(indexes_sql)
        result_list = cursor.fetchall()
        for result in result_list:
            indexes.append(result[0])
        cursor.close()
        return indexes
    
    def renew_statistics(self,dbname):
        '''
        Die Funktion wird nach dem Ersatz von Daten im Vek1 und Vek2 ausgeführt. So dass Statistiken jeweils aktuell sind, insbesondere auch für tagesaktuelle Geoprodukte.
        '''
        db = self.task_config['instances'][dbname]
        username = 'gdbp'
        password = self.task_config['users'][username]
        username = 'SYSOEM'
        connection = cx_Oracle.connect(username, password, db)
         
        index_tables = self.get_old_statistics(connection)
        
        db = self.task_config['instances'][dbname]
        username = 'geodb'
        password = self.task_config['users'][username]
        conn = cx_Oracle.connect(username, password, db)  
        cursor = conn.cursor()
        
        for index_table in index_tables:
            # alle Indices rebuilden (ausser Spatial Index und LOB-Index)
            indexes = self.get_indexes_of_table(index_table,connection)
            for index in indexes:
                #log.write("Rebuild Index " + index + "\n")
                index_sql = "ALTER INDEX " + index + " REBUILD" 
                cursor.execute(index_sql)

                cursor.callproc(name="dbms_stats.delete_table_stats", keywordParameters={'cascade_columns': True, 'cascade_indexes': True, 'ownname':'geodb', 'tabname': index_table})
                plsql = """ 
                    begin
                      dbms_stats.gather_table_stats(ownname=>'geodb', estimate_percent=>dbms_stats.auto_sample_size, cascade=>TRUE, method_opt=>'for all columns size repeat', tabname=>:table);
                    end;""" 
                cursor.execute(plsql, table=index_table)
        cursor.close()
        connection.close()
        conn.close()
        return 'OK'
    
    def start(self):
        '''
        Die aktuelle Funktion wird zu Beginn der Funktionsausführung
        (deshalb im Konstruktor) aus der Liste der ausgeführten
        entfernt. Sie wird erst am Schluss wieder eingefügt.
        '''
        if self.task_config.has_key("ausgefuehrte_funktionen"):
            if self.name in self.task_config['ausgefuehrte_funktionen']:
                self.task_config['ausgefuehrte_funktionen'].remove(self.name)
        
        
    def finish(self):
        '''
        erledigt Arbeiten, die am Schluss jeder Funktion gemacht werden müssen:
        - Task-Config in JSON-File schreiben
        - Die ausgeführte Funktion in der Task-Config als ausgeführt eintragen
        '''
        if not self.name in self.task_config['ausgefuehrte_funktionen']:
            self.task_config['ausgefuehrte_funktionen'].append(self.name)
        
        self.write_task_config()
        