# -*- coding: utf-8 -*-
'''
Created on 09.01.2015

@author: Peter Schär
'''
from .TemplateFunction import TemplateFunction
import os
import json

class Generierung(TemplateFunction):
    '''
    Sammelt sämtliche benötigten Informationen zusammen aus:
    - DataDictionary
    - General Config
    - GeoDBProzess
    Die Informationen werden in die task_config geschrieben.
    '''


    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"Generierung"
        
        TemplateFunction.__init__(self, logger, task_config)
        
        self.logger = logger
        self.task_config = task_config
                
        self.__load_task_config()
                
        self.__execute()
        self.logger.info(u"Task-Config nach execute: " + str(self.task_config))
        
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        #Diverse Einträge im task_config generieren
        if not self.task_config.has_key("ausgefuehrte_funktionen"):
            self.task_config['ausgefuehrte_funktionen'] = []

        
        self.finish()
      
       
    def __load_task_config(self):
        '''
        Lädt die Task-Config aus der JSON-Datei, sofern sie existiert
        und der task_override-Parameter True ist.
        '''
        js = ""
        task_config_file = self.task_config['task_config_file']
        if os.path.exists(task_config_file):
            if self.task_config['task_config_load_from_JSON']:
                f = open(task_config_file, "r")
                js = json.load(f)
                f.close
                
        if len(js) > 0:
                # die Variable js darf nicht einfach self.task_config
                # zugewiesen werden, da damit ein neues Objekt erzeugt
                # wird. self.task_config  ist dann in den Usecases nicht
                # mehr identisch. Damit kein neues Objekt erzeugt wird,
                # wird das bestehende geleert (clear) und dann mit den
                # Inhalten aus der Variable js gefüllt.
                self.task_config.clear()
                self.task_config.update(js)
                
