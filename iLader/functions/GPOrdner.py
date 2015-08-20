# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import os

class GPOrdner(TemplateFunction):
    '''
    Die Funktion erstellt auf dem Freigabeshare folgende Verzeichnisse neu:
    
    - Geoprodukt-Verzeichnis
    - Unterverzeichnis ``mxd``
    - Unterverzeichnis ``symbol``
    - Unterverzeichnis ``Zusatzdaten``
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "GPOrdner"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
            
    def __check_and_create_subdir(self, sub_dir):
        '''
        Prüft ob das angegebene Unterverzeichnis existiert und
        erstellt es nötigenfalls.
        :param subdir: Voller Pfad zum zu erstellenden Unterverzeichnis
        '''

        if os.path.exists(sub_dir):
            self.logger.info("Das Unterverzeichnis" + sub_dir + "existiert bereits. Es wird nicht neu angelegt.")
        else:
            self.logger.info("Das Unterverzeichnis" + sub_dir + "existiert noch nicht. Es wird neu angelegt.")
            os.makedirs(sub_dir)
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        #TODO: Verzeichnis Zusatzdaten erstellen
        # Verzeichnis-Pfade zusammensetzen
        gpr_dir = self.task_config['ziel']['ziel_begleitdaten_gpr']
        mxd_dir = os.path.join(gpr_dir, "mxd") #TODO: Verzeichnisname aus task_config auslesen
        symbol_dir = os.path.join(gpr_dir, "symbol") #TODO: Verzeichnisname aus task_config auslesen
        
        # Prüfen ob das Geoprodukt-Verzeichnis existiert
        if os.path.exists(gpr_dir):
            self.logger.info("Das Geoprodukt-Verzeichnis " + gpr_dir + " existiert bereits. Es wird nicht neu angelegt.")
            self.__check_and_create_subdir(mxd_dir)
            self.__check_and_create_subdir(symbol_dir)
        else:
            self.logger.info("Das Geoprodukt-Verzeichnis " + gpr_dir + " existiert noch nicht. Es wird neu angelegt.")
            os.makedirs(gpr_dir)
            self.__check_and_create_subdir(mxd_dir)
            self.__check_and_create_subdir(symbol_dir)
       
        self.finish()