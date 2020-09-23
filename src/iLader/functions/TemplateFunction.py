# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import json
import logging
import codecs

class TemplateFunction(object):
    '''
    Diese Klasse ist eine abstrakte Klasse, von der
    sämtliche Funktionen erben. Als abstrakte Klasse wird
    sie nie selber ausgeführt werden, sie dient nur als
    Vorlage und enthält Code, der von allen Funktionen
    geteilt wird.
    '''
    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.logger = logging.getLogger("iLaderLogger")
        self.task_config = task_config
        self.general_config = general_config
        
    def write_task_config(self):
        '''
        schreibt die aktuelle task_config in ein JSON-File.
        '''
        with codecs.open(self.task_config['task_config_file'], "w", "utf-8") as json_file:
            json.dump(self.task_config, json_file, indent=4)
        
    def start(self):
        '''
        Die aktuelle Funktion wird zu Beginn der Funktionsausführung
        (deshalb im Konstruktor) aus der Liste der ausgeführten
        entfernt. Sie wird erst am Schluss wieder eingefügt.
        '''
        if self.task_config.has_key("ausgefuehrte_funktionen"):
            if self.name in self.task_config['ausgefuehrte_funktionen']:
                self.task_config['ausgefuehrte_funktionen'].remove(self.name)
        
    def finish(self):
        '''
        erledigt Arbeiten, die am Schluss jeder Funktion gemacht werden müssen:
        - Task-Config in JSON-File schreiben
        - Die ausgeführte Funktion in der Task-Config als ausgeführt eintragen
        '''
        if not self.name in self.task_config['ausgefuehrte_funktionen']:
            self.task_config['ausgefuehrte_funktionen'].append(self.name)
        
        self.write_task_config()
        