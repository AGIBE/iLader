# -*- coding: utf-8 -*-
'''
Created on 09.01.2015

@author: Peter Schär
'''
import json

class TemplateFunction(object):
    '''
    Diese Klasse ist eine abstrakte Klasse, von der
    sämtliche Funktionen erben. Als abstrakte Klasse wird
    sie nie selber ausgeführt werden, sie dient nur als
    Vorlage und enthält Code, der von allen Funktionen
    geteilt wird.
    '''


    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.logger = logger
        self.task_config = task_config
        
        self.logger.info(u"Task-Config wird rausgeschrieben (" + self.task_config['task_config_file'] + ")")
        
        # Die aktuelle Funktion wird zu Beginn der Funktionsausführung
        # (deshalb im Konstruktor) aus der Liste der ausgeführten
        # entfernt. Sie wird erst am Schluss wieder eingefügt.
        if self.task_config.has_key("ausgefuehrte_funktionen"):
            if self.name in self.task_config['ausgefuehrte_funktionen']:
                self.task_config['ausgefuehrte_funktionen'].remove(self.name)
    
    def write_task_config(self):
        '''
        schreibt die aktuelle task_config in ein JSON-File.
        '''
        f = open(self.task_config['task_config_file'], "w")
        json.dump(self.task_config, f, indent=4)
        f.close()
        
    def finish(self):
        '''
        erledigt Arbeiten, die am Schluss jeder Funktion gemacht werden müssen:
        - Task-Config in JSON-File schreiben
        - Die ausgeführte Funktion in der Task-Config als ausgeführt eintragen
        '''
        if not self.name in self.task_config['ausgefuehrte_funktionen']:
            self.task_config['ausgefuehrte_funktionen'].append(self.name)
        
        self.write_task_config()
        