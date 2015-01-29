# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction

class QSStatus(TemplateFunction):
    '''
    Die Funktion ermittelt den Status der Qualitätssicherung. Die Qualitätssicherung
    besteht auf folgenden Funktionen und deren Stati in task_config:
    
    - Checkscript Normierung ``task_config["qs"]["checkscript_passed"]``
    - DeltaChecker ``task_config["qs"]["deltachecker_passed"]``
    - QA-Framework ``task_config["qs"]["qaframework_passed"]``
    
    Jede Funktion kann in task_config folgende Stati aufweisen:
    
    - ``"undefined"``: Funktion wurde nicht ausgeführt.
    - ``TRUE``: Funktion wurde ausgeführt, Rückgabewert ist ``TRUE``, es wurden keine Fehler gefunden
    - ``FALSE`` Funktion wurde ausgeführt, Rückgabewert ist ``TRUE``, es wurden Fehler gefunden
    
    Wenn einer der drei Bestandteile den Wert ``FALSE`` hat, werden folgende 
    Aktionen ausgeführt:

    - ``task_config["qs"]["qs_gesamt_passed"]=FALSE`` setzen
    - In der Tabelle ``tb_importe_geodb.status=1`` (geprüft) setzen
    
    In allen übrigen Fällen werden folgende Aktionen ausgeführt:
    
    - ``task_config["qs"]["qs_gesamt_passed"]=TRUE`` setzen
    - In der Tabelle ``tb_importe_geodb.status=4`` (geprüft) setzen
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"QSStatus"
        TemplateFunction.__init__(self, logger, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info(u"Funktion " + self.name + u" wird ausgelassen.")
        else:
            self.logger.info(u"Funktion " + self.name + u" wird ausgeführt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        
        self.logger.info(u"Die Funktion " + self.name + u" arbeitet vor sich hin")
        
       
        self.finish()