# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import md5
import arcpy

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
            
        
    def __delete_indices(self, table):
        '''
        Loescht alle attributiven Indices einer Tabelle. Nicht geloescht wird der raeumliche Index auf der Spalte shape sowie
        der attributive Index auf der Spalte objectid, der bereits beim Kopieren erstell wird.
        :param table: Vollstaendiger Pfad zur Tabelle bei der die Indices geloescht werden sollen.
        '''
        table_sp = table.split('.')
        indices_sql= "SELECT DISTINCT i.relname as index_name\
                    FROM pg_class t, pg_class i, pg_index ix, pg_attribute a\
                    WHERE t.oid = ix.indrelid and i.oid = ix.indexrelid and a.attrelid = t.oid and a.attnum = ANY(ix.indkey) and t.relkind = 'r' \
                    AND t.relname in ('" + table_sp[1] + "') and a.attname not in ('shape') "
        
        indices_results = self.general_config['connections']['VEK2_GEODB_PG'].db_read(indices_sql)
        
        if indices_results:
            for index in indices_results:
                self.logger.info("Loesche Index %s" % (index[0]))
                # Pruefen ob Primary Key
                if index[0].endswith('_pk'):
                    delete_index_sql = 'ALTER TABLE %s DROP CONSTRAINT %s' % (table, index[0])
                else:
                    delete_index_sql = 'DROP INDEX %s' % (index[0])
                self.general_config['connections']['VEK2_GEODB_PG'].db_read(delete_index_sql)


    def __execute(self):
        '''
        Fuehrt den eigentlichen Funktionsablauf aus.
        Iteriert durch alle Vektorebenen (inkl. Wertetabellen) und erstellt die dort
        aufgefuehrten Indizes fuer die Instanz vek2.
        '''
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
            self.logger.info("Loesche bestehende Indices fuer %s im vek2." % (ebename))
            self.__delete_indices(table)

            # Primary Key erstellen
            if not pk:
                self.logger.info("Erstelle Primary Key fuer %s im vek2." % (ebename))
                pk_attributes = pk.fields
                if len(pk_attributes) == 1:
                    pk_attribute = pk_attributes[0].name.lower()
                    createpk_sql = "ALTER TABLE %s ADD CONSTRAINT %s_%s_pk PRIMARY KEY (%s)" % (table, ebename, pk_attribute, pk_attribute)
                    self.general_config['connections']['VEK2_GEODB_PG'].db_write(createpk_sql)
                elif len(pk_attributes) > 1:
                    self.logger.error("Primary Key konnte nicht erstellt werden fuer " + ebename + ", da PK auf mehrere Spalten verteilt. " + str(pk.name))
            
            #Restliche Indizes erstellen
            if len(ebene["indices"]) > 0:
                self.logger.info("Erstelle Index fuer %s im vek2." % (ebename))
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
                    createidx_sql = 'CREATE %s INDEX %s ON %s (%s)' % (indextyp, indexname, table, index_attribute)
                    self.general_config['connections']['VEK2_GEODB_PG'].db_write(createidx_sql)
       
        self.finish()