# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import shutil

class Begleitdaten(TemplateFunction):
    '''
    Kopiert sämtliche Legendenfiles (.lyr) und MXD-Dateien (.mxd) auf den
    Freigabeshare. Die Files sind in task_config referenziert:
    
    - ``task_config["legende"]``
    - ``task_config["mxd"]``
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"Begleitdaten"
        TemplateFunction.__init__(self, logger, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info(u"Funktion " + self.name + u" wird ausgelassen.")
        else:
            self.logger.info(u"Funktion " + self.name + u" wird ausgeführt.")
            self.start()
            self.__execute()
            
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus.
        shutil.filecopy überschreibt Files, die am Ziel bereits
        existieren. Also muss dies auch nicht vorgängig geprüft
        werden. Ob die Files alle vorhanden sind, wird in der
        Funktion CheckscriptNormierung bereits überprüft.
        '''
        # Legenden
        self.logger.info("Legendenfiles kopieren")
        for legende in self.task_config["legende"]:
            self.logger.info("Legende " + legende["name"] + " wird kopiert.")
            shutil.copyfile(legende["quelle"], legende["ziel"])
        
        # MXDs
        self.logger.info("MXD-Files kopieren")
        for mxd in self.task_config["mxd"]:
            self.logger.info(mxd["name"] + " wird kopiert.")
            shutil.copyfile(legende["quelle"], legende["ziel"])
        
       
        self.finish()