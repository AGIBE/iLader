# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import shutil

class Fonts(TemplateFunction):
    '''
    Kopiert allfällige Font-Dateien auf den Freigabeshare. Die Font-Dateien
    sind in task_config definiert:
    
    - ``task_config["font"]`` 
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Fonts"
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
        shutil.filecopy überschreibt Files, die am Ziel bereits
        existieren. Also muss dies auch nicht vorgängig geprüft
        werden. Ob die Files alle vorhanden sind, wird in der
        Funktion CheckscriptNormierung bereits überprüft.
        '''
        self.logger.info("Fonts kopieren")
        if len(self.task_config["font"]) > 0:
            for font in self.task_config["font"]:
                self.logger.info("Font %s wird kopiert." % (font["name"]))
                shutil.copyfile(font["quelle"], font["ziel_akt"])
                shutil.copyfile(font["quelle"], font["ziel_zs"])
        else:
            self.logger.info("Keine Fonts vorhanden. Es wird nichts kopiert.")
        
        self.finish()