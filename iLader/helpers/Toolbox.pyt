# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import arcpy
import cx_Oracle
from iLader.helpers import Crypter
from iLader.usecases import Usecase
import os
import configobj

#TODO: prüfen ob statt ArcGIS-Toolbox nicht ein GUI mit argparse und gooey einfacher wäre
class Toolbox(object):
    '''
    ArcGIS Python-Toolbox, mit der ein Import-Task in der Geoprocessing-
    Umgebung gestartet werden kann. Die Toolbox greift auf die iLader-
    Konfiguration zu, um die nötigen Infos aus dem DataDictionary aus-
    lesen zu können.
    
    Alle Tasks werden aus dem DataDictionary ausgelesen (wenn STATUS=1) und
    mit Zusatzinformationen (GPR-Code, Jahr, Version) im Geoprocessing-
    Dialog angezeigt.
     
    Hat der Anwender einen Taks ausgewählt, wird der entsprechende Usecase
    gestartet.
    '''
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
        sql = "SELECT t.TASK_OBJECTID, u.UC_BEZEICHNUNG, g.GPR_BEZEICHNUNG, z.GZS_JAHR, z.GZS_VERSION FROM " + schema + ".TB_TASK t LEFT JOIN " + schema + ".TB_USECASE u ON t.UC_OBJECTID=u.UC_OBJECTID LEFT JOIN " + schema + ".TB_GEOPRODUKT_ZEITSTAND z ON z.GZS_OBJECTID = t.GZS_OBJECTID LEFT JOIN " + schema + ".TB_GEOPRODUKT g ON z.GPR_OBJECTID = g.GPR_OBJECTID WHERE t.TASK_STATUS=1 ORDER BY g.GPR_BEZEICHNUNG ASC"
        
        dd_connection = cx_Oracle.connect(user, pw, db)
        cursor = dd_connection.cursor()
        cursor.execute(sql)
        task_query_result = cursor.fetchall()
        
        tasks = []
        
        for row in task_query_result:
            task_objectid = str(row[0]).decode('cp1252')
            uc_bezeichnung = str(row[1]).decode('cp1252')
            gpr_bezeichnung = str(row[2]).decode('cp1252')
            gzs_jahr = str(row[3]).decode('cp1252')
            gzs_version = str(row[4]).decode('cp1252')
            #Abmachung: alle Zeichen vor dem ersten Doppelpunkt entsprechen der Task-ID
            parameter_string = task_objectid + ": " + gpr_bezeichnung + " " + gzs_jahr + "_" + gzs_version + " (" + uc_bezeichnung + ")"
            
            tasks.append(parameter_string)
        
        cursor.close()
        dd_connection.close()    
        
        return tasks
        
    def getParameterInfo(self):
        
        param1 = arcpy.Parameter(
            displayName="Import-Task",
            name="import_task",
            datatype="GPString",
            parameterType="required",
            direction="Input"
        )
        
        param1.filter.list = self.__getImportTasks()
        
        param2 = arcpy.Parameter(
            displayName="Task-Config aus JSON-File einlesen?",
            name="load_task_config",
            datatype="GPBoolean",
            parameterType="required",
            direction="Input"
        )
        
        param2.value=False;
        
        params = [param1, param2]
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
        #Abmachung: alle Zeichen vor dem ersten Doppelpunkt entsprechen der Task-ID
        task_id = parameters[0].valueAsText.split(":")[0]
        load_task_config = parameters[1].value
        arcpy.AddMessage("Task-ID " + task_id + " wird ausgeführt.")
        uc = Usecase(task_id, load_task_config)
        uc.run()
        