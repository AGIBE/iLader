# -*- coding: utf-8 -*-
'''
Created on 09.01.2015

@author: Peter Schär
'''
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import iLader.helpers
import os
import configobj
import datetime

class TemplateUsecase(object):
    '''
    Diese Klasse ist eine abstrakte Klasse, von der
    sämtliche Usecases erben. Als abstrakte Klasse wird
    sie nie selber ausgeführt werden, sie dient nur als
    Vorlage und enthält Code, der von allen Usecases
    geteilt wird.
    '''


    def __init__(self, task_id, task_config_load_from_JSON):        
        '''
        Constructor
        :param task_id: Eindeutige ID des auszuführenden Tasks, stammt aus TB_IMPORTE_GEODB.task_id
        :param task_config_load_from_JSON: soll die Task-Konfiguration neu generiert werden (TRUE) oder nicht (FALSE)
        '''
        self.task_id = int(task_id)
        self.task_config_load_from_JSON = task_config_load_from_JSON
        
        # Allgemeine und task-spezifische Konfiguration initialisieren
        self.general_config = self.__init_generalconfig()
        self.task_config = self.__init_taskconfig()
        
        # Logger initialisieren
        self.logger = self.__init_logging()
        
        self.logger.info(u"Usecase " + self.name + " initialisiert.")
        self.logger.info(u"Task-Id: " + unicode(self.task_id))
        self.logger.info(u"Task-Directory: " + self.task_config['task_directory'])
        self.logger.info(u"Log-File: " + self.task_config['log_file'])
    
    def __create_loghandler_file(self, filename):
        '''
        Konfiguriert einen File-Loghandler
        :param filename: Name (inkl. Pfad) des Logfiles 
        '''
        
        file_formatter = logging.Formatter('%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', '%Y-%m-%d %H:%M:%S')
        
        h = logging.FileHandler(filename, encoding="UTF-8")
        h.setLevel(logging.DEBUG)
        h.setFormatter(file_formatter)
        
        return h
    
    def __create_loghandler_arcgis(self):
        '''
        Konfiguriert einen ArcGIS-Loghandler
        Inspiriert durch: http://ideas.arcgis.com/ideaView?id=087E00000004H3yIAE
        '''
        # Das gewünschte Format der Log-Message wird definiert
        arcpy_formatter = logging.Formatter('%(asctime)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        
        h = iLader.helpers.ArcGISLogHandler()
        h.setFormatter(arcpy_formatter)
        h.setLevel(logging.DEBUG)
        
        return h
    
    def __init_logging(self):
        '''
        Der Logger wird mit zwei Handlern (arcpy und file) initialisiert
        '''
        logger = logging.getLogger("iLaderLogger")
        logger.setLevel(logging.DEBUG)
        
        # Diese leere Initialisierung ist notwendig, damit der Logger
        # mehrfach in einer Session aufgerufen werden kann. Ansonsten
        # gibt es einen Fehler
        # inspiriert durch: http://ideas.arcgis.com/ideaView?id=087E00000004H3yIAE
        logger.handlers = []
        
        logger.addHandler(self.__create_loghandler_arcgis())
        logger.addHandler(self.__create_loghandler_file(self.task_config['log_file']))
        
        return logger
    
    def __get_general_configfile_from_envvar(self):
        '''
        Holt den Pfad zur Konfigurationsdatei aus der Umgebungsvariable
        GEODBIMPORTHOME und gibt dann den vollständigen Pfad (inkl. Dateiname)
        der Konfigurationsdatei zurück.
        '''
        config_directory = os.environ['GEODBIMPORTHOME']
        config_filename = "config.ini"
        
        config_file = os.path.join(config_directory, config_filename)
        
        return config_file
    
    def __create_task_dir(self, task_dir, log_file, archive_log_file):
        '''
        Erzeugt das Logfile (inkl. des Taskverzeichnisses). Wenn das Logfile schon existiert,
        wird das bestehende Logfile umbenannt.
        :param task_dir: Taskverzeichnis
        :param log_file: Dateiname des Logfiles
        :param archive_log_file: Name des umbenannten Logfiles
        '''
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)
        else:
            if os.path.exists(log_file):
                os.rename(log_file, archive_log_file)
    
    def __init_taskconfig(self):
        '''
        Initialisiert den Taskconfig-Dictionary mit den ersten Werten und
        erstellt das Task-Verzeichnis, falls es noch nicht existiert.
        '''
        d = {}
        d['task_id'] = self.task_id
        d['task_config_load_from_JSON'] = self.task_config_load_from_JSON
        
        task_dir = os.path.join(self.general_config['task_verzeichnis'], str(self.task_id))
        
        task_config_file = os.path.join(task_dir, str(self.task_id) + ".json")

        log_file_name = str(self.task_id) + ".log"
        log_file = os.path.join(task_dir, log_file_name)
        
        # Falls das Log-File umbenannt werden muss, wird hier der Name gebildet
        archive_log_file_name = str(self.task_id) + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_log_file = os.path.join(task_dir, archive_log_file_name)
        
        # Task-Verzeichnis erstellen, falls es noch nicht existiert
        # Falls es existiert, das dort liegende Log-File umbenennen
        self.__create_task_dir(task_dir, log_file, archive_log_file)
                
        d['task_directory'] = task_dir
        d['log_file'] = log_file
        d['task_config_file'] = task_config_file
        
        return d
    
    def __decrypt_passwords(self, section, key):
        '''
        Entschlüsselt sämtliche Passworte in der zentralen
        Konfigurationsdatei. Wird aus der ConfigObj.walk-Funktion
        aus aufgerufen. Deshalb sind section und key als
        Parameter obligatorisch.
        :param section: ConfigObj.Section-Objekt
        :param key: aktueller Schlüssel
        '''
        if key == "password":
            section[key] = "UNVERSCHLUESSELT"
        
    
    def __init_generalconfig(self):
        '''
        liest die zentrale Konfigurationsdatei in ein ConfigObj-Objet ein.
        Dieser kann wie ein Dictionary gelesen werden.
        '''
        config_filename = self.__get_general_configfile_from_envvar()
        config_file = configobj.ConfigObj(config_filename, encoding="UTF-8")
        
        # Die Walk-Funktion geht rekursiv durch alle
        # Sections und Untersections der Config und 
        # ruft für jeden Key die angegebene Funktion
        # auf
        config_file.walk(self.__decrypt_passwords)
        
        return config_file
        
