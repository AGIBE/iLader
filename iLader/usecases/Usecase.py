# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import chromalog
import os
import datetime
import cx_Oracle
from iLader.functions import *
import iLader.helpers.Helpers
import sys

class Usecase():
    '''
    Allgemeine Usecase-Klasse, über die sämtliche Usecases ausgeführt werden.
    Die Klasse liest via TB_TASK den Usecase aus und basierend darauf die
    auszuführenden Funktionen aus TB_FUNCTION und TB_USECASE_FUNCTION.
    Daraufhin werden die Funktionen ausgeführt.
    Die Funktionen Generierung und Ausputzer haben einen speziellen Status.
    Sie werden in jedem Fall (d.h. in jedem Usecase) ausgeführt.
    '''
    
    def __init__(self, task_id, task_config_load_from_JSON):
        '''
        Constructor
        :param task_id: Eindeutige ID des auszuführenden Tasks, stammt aus TB_IMPORTE_GEODB.task_id
        :param task_config_load_from_JSON: soll eine existierende Task-Config eingelesen (TRUE) oder neu erzeugt werden (FALSE)
        '''
        self.task_id = int(task_id)
        self.task_config_load_from_JSON = task_config_load_from_JSON
        
        # Allgemeine und task-spezifische Konfiguration initialisieren
        self.general_config = iLader.helpers.Helpers.init_generalconfig()
        self.task_config = self.__init_taskconfig()
        
        # Logger initialisieren
        self.logger = self.__init_logging()
        
        #self.logger.info(u"Usecase " + self.name + " initialisiert.")
        self.logger.info(u"Task-Id: " + unicode(self.task_id))
        self.logger.info(u"Task-Directory: " + self.task_config['task_directory'])
        self.logger.info(u"Log-File: " + self.task_config['log_file'])
            
    def run(self):
        self.logger.info(u"Start der Funktionsausführung")
        try:            
            f = Generierung(self.logger, self.task_config, self.general_config)
            self.logger.info(u"Funktion " + f.name + u" wurde ausgeführt")
    
            auszufuehrende_funktionen = self.__get_functions_to_execute()
            
            for funktion in auszufuehrende_funktionen:
                funktionsklasse = globals()[funktion]
                f = funktionsklasse(self.logger, self.task_config)
                self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
                
            self.logger.info("Der Import-Task " + unicode(self.task_id) + " wurde erfolgreich durchgeführt!")
        except Exception as e:
            self.logger.error(e.message.decode("iso-8859-1"))
        finally: # Die Ausputzer-Funktion muss immer ausgeführt werden.
            f = Ausputzer(self.logger, self.task_config)
            self.logger.info(u"Funktion " + f.name + u" wurde ausgeführt")
            
    def __get_functions_to_execute(self):
        db = self.task_config['instances']['team']
        schema = self.task_config['schema']['geodb_dd']
        username = 'geodb_dd'
        password = self.task_config['users'][username]
        functions = []
        
        sql_usecase = "select uc_objectid, uc_bezeichnung from " + schema + ".tb_usecase where uc_objectid in (select uc_objectid from " + schema + ".tb_task where task_objectid=" + unicode(self.task_id) + ")"

        connection = cx_Oracle.connect(username, password, db)  
        cursor = connection.cursor()
        cursor.execute(sql_usecase)
        
        row = cursor.fetchone()
        uc_objectid = row[0]
        uc_bezeichnung = row[1].decode("iso-8859-1")
        self.name = uc_bezeichnung
        sql_functions = "SELECT " + schema + ".tb_function.fct_classname FROM " + schema + ".tb_usecase_function JOIN " + schema + ".tb_function on " + schema + ".tb_usecase_function.fct_objectid = " + schema + ".tb_function.fct_objectid where UC_OBJECTID=" + unicode(uc_objectid) + " order by " + schema + ".tb_function.FCT_ORDER"
        cursor.execute(sql_functions)
        
        rows = cursor.fetchall()
        for row in rows:
            functions.append(row[0])
        
        cursor.close()
        connection.close()
        return functions
    
    def __create_loghandler_stream(self):
        '''
        Konfiguriert einen Stream-Loghandler. Der Output
        wird in sys.stdout ausgegeben. In der Regel ist das
        die Kommandozeile. Falls sys.stdout dies unterstützt,
        werden Warnungen und Fehler farbig ausgegeben (dank
        des chromalog-Moduls).
        '''
        
        file_formatter = chromalog.ColorizingFormatter('%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', '%Y-%m-%d %H:%M:%S')
        
        h = chromalog.ColorizingStreamHandler(stream=sys.stdout)
        h.setLevel(logging.DEBUG)
        h.setFormatter(file_formatter)
        
        return h
    
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
        Der Logger wird mit drei Handlern (arcpy, file und stream) initialisiert
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
        logger.addHandler(self.__create_loghandler_stream())
        
        return logger
    
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
        
        task_dir = os.path.join(self.general_config['task_verzeichnis'], unicode(self.task_id))
        
        task_config_file = os.path.join(task_dir, unicode(self.task_id) + ".json")

        log_file_name = unicode(self.task_id) + ".log"
        log_file = os.path.join(task_dir, log_file_name)
        
        # Falls das Log-File umbenannt werden muss, wird hier der Name gebildet
        archive_log_file_name = unicode(self.task_id) + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_log_file = os.path.join(task_dir, archive_log_file_name)
        
        # Task-Verzeichnis erstellen, falls es noch nicht existiert
        # Falls es existiert, das dort liegende Log-File umbenennen
        self.__create_task_dir(task_dir, log_file, archive_log_file)
                
        d['task_directory'] = task_dir
        d['log_file'] = log_file
        d['task_config_file'] = task_config_file
        
        return d