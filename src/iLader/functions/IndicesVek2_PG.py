# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import md5
import arcpy
from iLader.helpers import PostgresHelper

class IndicesVek2_PG(TemplateFunction):
    '''
    Fuer alle nach vek2 (PostgreSQL) kopierten Vektorebenen, erstellt diese Funktion
    die Attribut-Indices. Die Angaben zu den Ebenen und Indices sind
    in task_config abgelegt:
    
    - ``task_config["vektor_ebenen"]``

    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "IndicesVek2_PG"
        TemplateFunction.__init__(self, task_config, general_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgefuehrt.")
            self.start()
            self.__execute()
            
        
    def __delete_indices(self, host, db, db_user, port, pw, table):
        '''
        Loescht alle attributiven Indices einer Tabelle. Nicht geloescht wird der raeumliche Index auf der Spalte shape sowie
        der attributive Index auf der Spalte objectid, der bereits beim Kopieren erstell wird.
        :param table: Vollstaendiger Pfad zur Tabelle bei der die Indices geloescht werden sollen.
        '''
        table_sp = table.split('.')
        sql_query= "SELECT DISTINCT i.relname as index_name\
                    FROM pg_class t, pg_class i, pg_index ix, pg_attribute a\
                    WHERE t.oid = ix.indrelid and i.oid = ix.indexrelid and a.attrelid = t.oid and a.attnum = ANY(ix.indkey) and t.relkind = 'r' \
                    AND t.relname in ('" + table_sp[1] + "') and a.attname not in ('shape') "
        
        indices = PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query, True, True)
        
        if indices:
            for index in indices:
                self.logger.info("Loesche Index " + index[0])
                # Pruefen ob Primary Key
                if index[0].endswith('_pk'):
                    sql_query = 'ALTER TABLE ' + table + ' DROP CONSTRAINT ' + index[0]
                else:
                    sql_query = 'DROP INDEX ' + index[0]
                PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query)


    def __execute(self):
        '''
        Fuehrt den eigentlichen Funktionsablauf aus.
        Iteriert durch alle Vektorebenen (inkl. Wertetabellen) und erstellt die dort
        aufgefuehrten Indizes fuer die Instanz vek2.
        '''
        db = self.task_config['db_vek2_pg']
        port = self.task_config['port_pg']
        host = self.task_config['instances']['oereb']
        db_user = 'geodb'
        pw = self.task_config['users']['geodb']
        
        for ebene in self.task_config['vektor_ebenen']:    
            table = ebene['ziel_vek1'].lower().rsplit('\\',1)[1]
            ebename = ebene['gpr_ebe'].lower()
            pk = False
            
            # Liste Primary Keys auf
            indices = arcpy.ListIndexes(ebene['quelle'])
            for index in indices:
                if ("SDE_ROWID_UK" in index.name.upper()):
                    pk = index
            
            # Indices loeschen
            self.logger.info("Loesche bestehende Indices fuer " + ebename + " im vek2.")
            self.__delete_indices(host, db, db_user, port, pw, table)

            # Primary Key erstellen
            if pk is not False:
                self.logger.info("Erstelle Primary Key fuer " + ebename + " im vek2.")
                pk_attributes = pk.fields
                if len(pk_attributes) == 1:
                    pk_attribute = pk_attributes[0].name.lower()
                    sql_query = 'ALTER TABLE ' + table + ' ADD CONSTRAINT ' + ebename + '_' + pk_attribute + '_pk PRIMARY KEY (' + pk_attribute + ')'
                    PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query)
                elif len(pk_attributes) > 1:
                    self.logger.error("Primary Key konnte nicht erstellt werden fuer " + ebename + ", da PK auf mehrere Spalten verteilt. " + str(pk.name))
            
            #Restliche Indizes erstellen
            if len(ebene["indices"]) > 0:
                self.logger.info("Erstelle Index fuer " + ebename + " im vek2.")
                for index in ebene["indices"]:
                    # Jeden Index erstellen
                    index_attribute = index['attribute'].lower()
                    hashfunc = md5.new(table.upper() + "." + index_attribute.upper())
                    indexname = "geodb_" + hashfunc.hexdigest()[0:10]
                    if index['unique'] == "False":
                        indextyp = ''
                    elif index['unique'] == "True":
                        indextyp = 'UNIQUE'
                    self.logger.info("Index: " + index_attribute + ": " + indextyp) 
                    sql_query = 'CREATE ' + indextyp + ' INDEX ' +indexname + ' ON ' + table + ' (' + index_attribute + ')'
                    PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query)
       
        self.finish()