# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import shutil
import os

class Zusatzdaten(TemplateFunction):
    '''
    Kopiert ein allfällig vorhandenes Zusatzdaten-Verzeichnis auf den
    Freigabeshare. Dort wird es zusätzlich in einen neuen Ordner mit
    Zeitstands-Angabe kopiert. Die Angaben sind in task_config abgelegt:
    
    - ``task_config["zusatzdaten"]``
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Zusatzdaten"
        TemplateFunction.__init__(self, logger, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
        
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus.
        Weil shutil.copytree einen Fehler zurückgibt, 
        wenn das Zielverzeichnis bereits existiert,
        wird vorgängig geprüft, ob das Zielverzeichnis
        existiert und nötigenfalls gelöscht.
        '''
        
        if len(self.task_config["zusatzdaten"]) > 0:
            src_dir = self.task_config["zusatzdaten"]["quelle"]
            target_dir = self.task_config["zusatzdaten"]["ziel"]
            if os.path.exists(target_dir):
                self.logger.info("Zielverzeichnis " + target_dir + " existiert bereits. Es wird gelöscht.")
                shutil.rmtree(target_dir)
            self.logger.info("Zusatzdaten-Verzeichnis " + src_dir + " wird nach " + target_dir + " kopiert.")
            shutil.copytree(src_dir, target_dir)
        else:
            self.logger.info("Keine Zusatzdaten vorhanden. Es wird nichts kopiert.")
        
        self.finish()