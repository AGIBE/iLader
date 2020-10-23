# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import shutil

class Styles(TemplateFunction):
    '''
    Kopiert allfällige Style-Dateien auf den Freigabeshare. Die Style-Dateien
    sind in task_config definiert:
    
    - ``task_config["style"]`` 
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Styles"
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
        
        # Styles
        self.logger.info("Styles kopieren")
        if len(self.task_config["style"]) > 0:
            for style in self.task_config["style"]:
                self.logger.info("Style %s wird kopiert." % (style["name"]))
                shutil.copyfile(style["quelle"], style["ziel_akt"])
                shutil.copyfile(style["quelle"], style["ziel_zs"])
        else:
            self.logger.info("Keine Styles vorhanden. Es wird nichts kopiert.")
        
        self.finish()