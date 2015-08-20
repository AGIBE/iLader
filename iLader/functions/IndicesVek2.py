# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import md5
import arcpy

class IndicesVek2(TemplateFunction):
    '''
    Für alle nach Vek2 kopierten Vektorebenen erstellt diese Funktion
    die Attribut-Indices. Die Angaben zu den Ebenen und Indices sind
    in task_config abgelegt:
    
    - ``task_config["vektor_ebenen"]``
    
    Ob die Indices mit arcpy oder mit Oracle-Funktionen erstellt werden
    sollen, ist noch festzulegen.
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "IndicesVek2"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus.
        Iteriert durch alle Vektorebenen (inkl. Wertetabellen) und erstellt die dort
        aufgeführten Indizes für die Instanz VEK2.
        '''
        for ebene in self.task_config['vektor_ebenen']:
                if len(ebene["indices"]) > 0:
                    target = ebene['ziel_vek2']
                    ebename = ebene['gpr_ebe']
                    self.logger.info("Erstelle Index für " + ebename + " im VEK2.")           
                    for index in ebene["indices"]:
                        try:
                            self.logger.info("Index: ") 
                            index_attribute = index['attribute'].replace(", ", ";")
                            hashfunc = md5.new(ebename.upper() + "." + index_attribute.upper())
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
       
        self.finish()