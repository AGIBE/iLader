# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import logging

class Ausputzer(TemplateFunction):
    '''
    Diese Funktion führt am Ende eines Imports/Tasks bestimmte
    Aufräumarbeiten aus:
    - Connection-Files löschen
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Ausputzer"
        TemplateFunction.__init__(self, task_config)
        
        # Der Abschnitt kann wahrscheinlich entfallen, da die Funktion
        # immer ausgeführt wird.
        # if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
        #     self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        # else:
        #     self.logger.info("Funktion " + self.name + " wird ausgeführt.")
        #     self.start()
        
        self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        self.finish()

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
