# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import json
from iLader.helpers.Crypter import Crypter
import copy
import logging

class TemplateFunction(object):
    '''
    Diese Klasse ist eine abstrakte Klasse, von der
    sämtliche Funktionen erben. Als abstrakte Klasse wird
    sie nie selber ausgeführt werden, sie dient nur als
    Vorlage und enthält Code, der von allen Funktionen
    geteilt wird.
    '''


    def __init__(self, task_config):
        '''
        Constructor
        
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.logger = logging.getLogger("iLaderLogger")
        self.task_config = task_config
        
    def write_task_config(self):
        '''
        schreibt die aktuelle task_config in ein JSON-File.
        '''
        f = open(self.task_config['task_config_file'], "w")
        # Alle Passwörter in der task_config müssen vor dem
        # Rausschreiben verschlüsselt werden. Damit sind sie
        # nur im Memory im Klartext vorhanden.
        # Deepcopy ist nötig, damit auch wirklich eine Kopie
        # des gesamten Dicts (inkl. aller verschachtelter
        # Objekte) gemacht wird.
        encrypted_task_config = copy.deepcopy(self.task_config)
        crypter = Crypter()
        for key, value in encrypted_task_config['users'].iteritems():
            encrypted_task_config['users'][key] = crypter.encrypt(value) 
                       
        json.dump(encrypted_task_config, f, indent=4)
        f.close()
        
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
        