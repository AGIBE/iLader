# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import md5
import arcpy

class IndicesVek3(TemplateFunction):
    '''
    Für alle nach Vek3 kopierten Vektorebenen erstellt diese Funktion
    die Attribut-Indices. Die Angaben zu den Ebenen und Indices sind
    in task_config abgelegt:
    
    - ``task_config["vektor_ebenen"]``
    
    Ob die Indices mit arcpy oder mit Oracle-Funktionen erstellt werden
    sollen, ist noch festzulegen.
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "IndicesVek3"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
        
    def __delete_indices(self, table):
        '''
        Löscht alle attributiven Indices einer Tabelle/Featureclass. Nicht gelöscht wird der räumliche Index sowie
        der attributive Index auf der Spalte OBJECTID, den ArcSDE selbständig anlegt.
        :param table: Vollständiger Pfad zur Tabelle/Featureclass bei der die Indices gelöscht werden sollen.
        '''
        indices = arcpy.ListIndexes(table)
        for index in indices:
            if ("SDE_ROWID_UK" not in index.name.upper()) and (not index.name.upper().endswith("_IX1")) and (not index.name.upper().startswith("UUID_")):
                self.logger.info("Lösche Index " + index.name)
                try:
                    arcpy.RemoveIndex_management(table, index.name)
                except Exception as e:
                    self.logger.warn("Fehler beim Löschen des Index " + index.name)
                    self.logger.info(e)

    def __deleteExistingIndex(self, tablename, attributname):
        '''
        Löscht Index auf ein Attribut, falls dieser vorhanden ist.
        :param tablename: Vollständiger Pfad zur Tabelle/Featureclass bei der der Index gelöscht werden sollen.
        :param attributname: Attributname der auf einen bestehenden Index geprüft werden soll.
        ''' 
        tabledescription = arcpy.Describe(tablename)
         
        for iIndex in tabledescription.indexes:
            if (iIndex.Fields[0].Name == attributname):
                try:
                    arcpy.RemoveIndex_management(tablename, iIndex.Name)
                    self.logger.info("Lösche Join- oder Relate-Index " + iIndex.name)
                except Exception as e:
                    self.logger.warn("Fehler beim Löschen des Join oder Relate-Index " + iIndex.name)
                    self.logger.warn(e)
                    
    def __execute(self):
        '''
        Iteriert durch alle Vektorebenen (inkl. Wertetabellen) und erstellt die dort
        aufgeführten Indizes für die Instanz VEK3.
        '''
        for ebene in self.task_config['vektor_ebenen']:
                target = ebene['ziel_vek3']
                ebename = ebene['gpr_ebe']
                table = target.rsplit('\\',1)[1]

                self.logger.info("Lösche bestehende Indices für " + ebename + " im VEK3.")
                self.__delete_indices(target)

                if len(ebene["indices"]) > 0:
                    self.logger.info("Erstelle Index für " + ebename + " im VEK3.")           
                    for index in ebene["indices"]:
                        try:
                            self.logger.info("Index: ") 
                            index_attribute = index['attribute'].replace(", ", ";")
                            hashfunc = md5.new(table.upper() + "." + index_attribute.upper())
                            indexname = "GEODB_" + hashfunc.hexdigest()[0:10]
                            if index['unique'] == "False":
                                indextyp = 'NON_UNIQUE'
                            elif index['unique'] == "True":
                                indextyp = 'UNIQUE'
                            arcpy.AddIndex_management(target, index_attribute, indexname, indextyp, "")
                            self.logger.info(index_attribute + ": " + indextyp)
                        except Exception as e:
                            self.logger.info("Fehler bei der Erstellung des Index " + index_attribute + ", " + indextyp)
                            self.logger.info(e)
        
                # Indices für Join und Relate-Felder
                if len(ebene["indices_join"]) > 0:
                    self.logger.info("Erstelle Join- oder Relate-Index für " + ebename + " im VEK3.")
                    for index in ebene["indices_join"]:
                        try:
                            self.logger.info("Index (Join & Relate-Felder): ") 
                            index_attribute = index['attribute'].replace(", ", ";")
                            hashfunc = md5.new(index['table'].upper() + "." + index_attribute.upper())
                            indexname = "GEODB_" + hashfunc.hexdigest()[0:10]
                            if index['unique'] == "False":
                                indextyp = 'NON_UNIQUE'
                            elif index['unique'] == "True":
                                indextyp = 'UNIQUE'
                            self.__deleteExistingIndex(target, index_attribute)
                            arcpy.AddIndex_management(target, index_attribute, indexname, indextyp, "")
                            self.logger.info(index_attribute + ": " + indextyp)
                        except Exception as e:
                            self.logger.warn("Fehler bei der Erstellung des Index " + index_attribute + ", " + indextyp)
                            self.logger.warn(e)
                                   
        self.finish()