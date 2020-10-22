# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import logging

class Ausputzer(TemplateFunction):
    '''
    Diese Funktion führt am Ende eines Imports/Tasks bestimmte
    Aufräumarbeiten aus:
    - Connection-Files löschen
    - Logging herunterfahren
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Ausputzer"
        TemplateFunction.__init__(self, task_config, general_config)
        
        self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        self.finish()

        self.logger.info("Lösche alle temporären SDE-Connectionfiles")
        for v in self.general_config['connections'].values():
            for cf in v.connection_files:
                self.logger.info(cf)
            v.delete_all_sde_connections()

        # Das Schliessen der Handler muss ganz am Schluss passieren,
        # damit danach keine Zugriffe darauf erfolgen und es zu Fehlern
        # kommt.
        # V.a. der FileHandler muss geschlossen werden, da sonst bei der
        # Ausführung in der ArcGIS-Toolbox File-Locks ein mehrfaches Aus-
        # führen verhindern.        
        self.logger.info("Das Logging-System wird heruntergefahren.")
        self.logger.info("Die Applikation wird beendet.")
        for hdl in self.logger.handlers:
            hdl.close()

