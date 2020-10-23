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

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Zusatzdaten"
        TemplateFunction.__init__(self, task_config, general_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['resume']:
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
            try:
                src_dir = self.task_config["zusatzdaten"]["quelle"]
                # workaround: nach löschen kann selbes Verzeichnis sonst nicht kopiert werden.
                target_dir_rm = self.task_config["zusatzdaten"]["ziel"]
                target_dir = self.task_config["zusatzdaten"]["ziel"]
                if os.path.exists(target_dir):
                    self.logger.info("Zielverzeichnis " + target_dir_rm + " existiert bereits. Es wird gelöscht.")
                    shutil.rmtree(target_dir_rm)
                self.logger.info("Zusatzdaten-Verzeichnis " + src_dir + " wird nach " + target_dir + " kopiert.")
                shutil.copytree(src_dir, target_dir)
            except OSError as e:
                self.logger.error("Zusatzdaten konnten nicht kopiert werden: " + str(e))
        else:
            self.logger.info("Keine Zusatzdaten vorhanden. Es wird nichts kopiert.")
        
        self.finish()