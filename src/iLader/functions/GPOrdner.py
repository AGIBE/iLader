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
    
    Das Unterverzeichnis ``Zusatzdaten`` wird nicht erstellt. Es wird bei Bedarf
    durch die Funktion Zusatzdaten erstellt.
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "GPOrdner"
        TemplateFunction.__init__(self, task_config, general_config)
        
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
            self.logger.info("Das Unterverzeichnis %s existiert bereits. Es wird nicht neu angelegt." % (sub_dir))
        else:
            self.logger.info("Das Unterverzeichnis %s existiert noch nicht. Es wird neu angelegt." % (sub_dir))
            os.makedirs(sub_dir)
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        # Verzeichnis-Pfade zusammensetzen
        gpr_dir = self.task_config['ziel']['ziel_begleitdaten_gpr']
        mxd_dir = self.task_config['ziel']['ziel_begleitdaten_mxd']
        symbol_dir = self.task_config['ziel']['ziel_begleitdaten_symbol']
        
        # Prüfen ob das Geoprodukt-Verzeichnis existiert
        if os.path.exists(gpr_dir):
            self.logger.info("Das Geoprodukt-Verzeichnis %s existiert bereits. Es wird nicht neu angelegt." % (gpr_dir))
            self.__check_and_create_subdir(mxd_dir)
            self.__check_and_create_subdir(symbol_dir)
        else:
            self.logger.info("Das Geoprodukt-Verzeichnis %s existiert noch nicht. Es wird neu angelegt." % (gpr_dir))
            os.makedirs(gpr_dir)
            self.__check_and_create_subdir(mxd_dir)
            self.__check_and_create_subdir(symbol_dir)
       
        self.finish()