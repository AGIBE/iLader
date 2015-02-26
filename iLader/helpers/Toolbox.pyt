# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import arcpy
import cx_Oracle
from iLader.helpers import Crypter
from iLader.usecases import NeuesGeoprodukt
import os
import configobj
import sys

class Toolbox(object):
    def __init__(self):
        self.label = "iLader"
        self.alias = "iLader-Toolbox - GeoDB-Import"
        
        self.tools = [Import]
        
class Import(object):
    def __init__(self):
        self.label = "Geoprodukt importieren"
        self.description = "Mit diesem Tool wird ein Geoprodukt in die GeoDB importiert. Es werden nur diejenigen Geoprodukte zur Auswahl angeboten, die importierbar und dem jeweiligen PC zugewiesen sind"
        self.canRunInBackground = False
        
        self.general_config = self.__init_generalconfig()
        
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
    
    def __decrypt_passwords(self, section, key):
        '''
        Entschlüsselt sämtliche Passworte in der zentralen
        Konfigurationsdatei. Wird aus der ConfigObj.walk-Funktion
        aus aufgerufen. Deshalb sind section und key als
        Parameter obligatorisch.
        :param section: ConfigObj.Section-Objekt
        :param key: aktueller Schlüssel im ConfigObj-Objekt
        '''
        # Hilfsklasse für die Entschlüsselung
        
        # Annahme: alle Keys, die "password" heissen, enthalten zu entschlüsselnde Passwörter
        crypter = Crypter()
        if key == "password":
            encrypted_password = section[key]
            decrypted_password = crypter.decrypt(encrypted_password)
            # Wert in der Config ersetzen
            section[key] = decrypted_password
    
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
    
    def __getImportTasks(self):
        db = self.general_config['instances']['team']
        user = self.general_config['users']['geodb_dd']['username']
        pw = self.general_config['users']['geodb_dd']['password']
        schema = self.general_config['users']['geodb_dd']['schema']
        sql = "SELECT TASK_OBJECTID, GZS_OBJECTID, UC_OBJECTID From " + schema + ".TB_TASK"
        
        dd_connection = cx_Oracle.connect(user, pw, db)
        cursor = dd_connection.cursor()
        cursor.execute(sql)
        task_query_result = cursor.fetchall()
        
        tasks = []
        
        for row in task_query_result:
            tasks.append(str(row[0]).decode('cp1252'))
        
        cursor.close()
        dd_connection.close()    
        
        return tasks
        
    def getParameterInfo(self):
        
        param1 = arcpy.Parameter(
            displayName="Pfad",
            name="pfad",
            datatype="String",
            parameterType="required",
            direction="Input"
        )
        
        param1.filter.list = self.__getImportTasks()
        
        params = [param1]
        return params
    
    def isLicensed(self):
        licenseStatus = False        
        arcinfoStatus = arcpy.CheckProduct("arcinfo")
        arceditorStatus = arcpy.CheckProduct("arceditor")
        validStates = ["Available", "AlreadyInitialized"]
        
        if arcinfoStatus in validStates or arceditorStatus in validStates:
            licenseStatus = True

        return licenseStatus
    
    def updateParameters(self, parameters):
        return
    
    def execute(self, parameters, messages):
        task_id = parameters[0].valueAsText
        arcpy.AddMessage("Task-ID " + task_id + " wird ausgeführt.")
        uc = NeuesGeoprodukt(task_id, False)
        