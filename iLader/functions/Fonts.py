# -*- coding: utf-8 -*-
'''
Created on 14.01.2015

@author: Peter Schär
'''
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import shutil

class Fonts(TemplateFunction):
    '''
    Kopiert die Fonts
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"Fonts"
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
        
        # Fonts
        self.logger.info("Fonts kopieren")
        if self.task_config["font"] > 0:
            for font in self.task_config["font"]:
                self.logger.info("Font " + font["name"] + " wird kopiert.")
                shutil.copyfile(font["quelle"], font["ziel"])
        else:
            self.logger.info("Keine Fonts vorhanden. Es wird nichts kopiert.")
        
        self.finish()