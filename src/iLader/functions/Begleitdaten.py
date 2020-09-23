# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import shutil
import os

class Begleitdaten(TemplateFunction):
    '''
    Kopiert sämtliche Legendenfiles (.lyr) und MXD-Dateien (.mxd) auf den
    Freigabeshare. Die Files sind in task_config referenziert:
    
    - ``task_config["legende"]``
    - ``task_config["mxd"]``
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Begleitdaten"
        TemplateFunction.__init__(self, task_config, general_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
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
        # Legenden
        self.logger.info("Legendenfiles kopieren")
        for legende in self.task_config["legende"]:
            self.logger.info("Legende " + legende["name"] + " wird kopiert.")
            shutil.copyfile(legende["quelle"], legende["ziel_akt"])
            shutil.copyfile(legende["quelle"], legende["ziel_zs"])
        
        # Legenden für Rasterdatasets
        # Kopiere lyr-Files für Rasterdatasets, die separat abgelegt sind
        self.logger.info("Legendenfiles für Rasterdatasets kopieren (falls vorhanden)")
        if os.path.exists(self.task_config['quelle_begleitdatenraster']):
            for f in os.listdir(self.task_config['quelle_begleitdatenraster']):
                if f.endswith((".lyr",".LYR")):
                    self.logger.info("Rasterdataset-Legende " + f + " wird kopiert.")
                    shutil.copyfile(os.path.join(self.task_config['quelle_begleitdatenraster'],f), os.path.join(self.task_config['ziel']['ziel_begleitdaten_symbol'], 'AKTUELL_' + f))

        # MXDs
        self.logger.info("MXD-Files kopieren")
        for mxd in self.task_config["mxd"]:
            self.logger.info(mxd["name"] + " wird kopiert.")
            shutil.copyfile(mxd["quelle"], mxd["ziel_akt"])
            shutil.copyfile(mxd["quelle"], mxd["ziel_zs"])
        
       
        self.finish()