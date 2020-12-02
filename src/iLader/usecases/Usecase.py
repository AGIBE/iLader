# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
# Hier müssen sämtliche Funktionen importiert werden, 
# damit unten der Trick mit globals funktioniert
from iLader.functions import *
import iLader.helpers.Helpers
import os
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
    
    def __init__(self, task_id, resume):
        '''
        Constructor
        :param task_id: Eindeutige ID des auszuführenden Tasks, stammt aus TB_IMPORTE_GEODB.task_id
        :param resume: soll eine existierende Task-Config eingelesen (TRUE) oder neu erzeugt werden (FALSE)
        '''
        self.task_id = int(task_id)
        self.resume = resume
        
        # Allgemeine und task-spezifische Konfiguration initialisieren
        self.general_config = iLader.helpers.Helpers.get_config()
        self.task_config = self.__init_taskconfig()
        
        # Logger initialisieren
        self.logger = AGILib.agilogger.initialize_agilogger(logfile_name=self.task_config['log_file_name'], logfile_folder=self.task_config['task_directory'], list_log_handler=['file','stream'], archive=True, logger_name="iLaderLogger")
        self.logger.info("Task-Id: " + unicode(self.task_id))
        self.logger.info("Task-Directory: " + self.task_config['task_directory'])
        self.logger.info("Log-File: " + self.task_config['log_file'])
        
        # Installation registrieren
        iLader.helpers.Helpers.register_installations(self.general_config, self.logger)

        # Connection-Files ausgeben
        self.logger.info("Folgende Connection-Files wurden angelegt:")
        for connection_file in self.general_config['connection_files'].values():
            self.logger.info(connection_file)
        
        self.is_task_valid = self.__get_task_status()
            
    def run(self):
        if self.is_task_valid:
            self.logger.info("Start der Funktionsausführung")
            f = Generierung(self.task_config, self.general_config)
            self.logger.info("Funktion " + f.name + " wurde ausgeführt")
    
            auszufuehrende_funktionen = self.__get_functions_to_execute()
            
            for funktion in auszufuehrende_funktionen:
                funktionsklasse = globals()[funktion]
                f = funktionsklasse(self.task_config, self.general_config)
                self.logger.info("Usecase "+ self.name + ": Funktion " + f.name + " wurde ausgeführt")
                
            self.logger.info("Der Import-Task " + unicode(self.task_id) + " wurde erfolgreich durchgeführt!")
            print("Import SUCCESSFUL!")
        else:
            self.logger.error("Task-ID " + unicode(self.task_id) + " ist nicht gültig!")
            self.logger.error("Import wird abgebrochen")
            raise ValueError("Task-ID ist nicht gültig!")
            
    def __get_task_status(self):
        '''
        Prüft ob der übergebene Import-Task gültig ist, d.h. ob er
        überhaupt in der Tabelle TB_TASK enthalten ist und ob er den
        Status 1 oder 2 aufweist.
        '''
        status_query = "SELECT TASK_STATUS FROM TB_TASK where TASK_OBJECTID=" + unicode(self.task_config['task_id'])
        task_status = False
        query_result = self.general_config['connections']['TEAM_GEODB_DD_ORA'].db_read(status_query)
        if len(query_result) == 1:
            tb_task_status = query_result[0][0]
            if tb_task_status in (1,2):
                task_status = True
        return task_status
            
    def __get_functions_to_execute(self):
        # Zunächst den Usecase auslesen
        usecase_sql = "select uc_objectid, uc_bezeichnung from tb_usecase where uc_objectid in (select uc_objectid from tb_task where task_objectid=" + unicode(self.task_id) + ")"
        usecase_result = self.general_config['connections']['TEAM_GEODB_DD_ORA'].db_read(usecase_sql, fetchall=False)
        uc_objectid = usecase_result[0]
        self.name = usecase_result[1]

        # Nun alle Funktionen dieses Usecases auslesen
        functions_sql = "SELECT tb_function.fct_classname FROM tb_usecase_function JOIN tb_function on tb_usecase_function.fct_objectid = tb_function.fct_objectid where UC_OBJECTID=" + unicode(uc_objectid) + " order by tb_function.FCT_ORDER"
        functions_result = self.general_config['connections']['TEAM_GEODB_DD_ORA'].db_read(functions_sql)
        functions = [function[0] for function in functions_result]
        return functions
    
    def __init_taskconfig(self):
        '''
        Initialisiert den Taskconfig-Dictionary mit den ersten Werten und
        erstellt das Task-Verzeichnis, falls es noch nicht existiert.
        '''
        d = {}
        d['task_id'] = self.task_id
        d['resume'] = self.resume
        
        task_dir = os.path.join(self.general_config['task_verzeichnis'], unicode(self.task_id))
        # Task-Verzeichnis erstellen, falls es noch nicht existiert
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)
        
        task_config_file = os.path.join(task_dir, unicode(self.task_id) + ".json")

        log_file_name = unicode(self.task_id) + ".log"
        log_file = os.path.join(task_dir, log_file_name)
              
        d['task_directory'] = task_dir
        d['log_file'] = log_file
        d['log_file_name'] = log_file_name
        d['task_config_file'] = task_config_file
        
        return d