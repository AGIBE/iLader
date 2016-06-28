# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import arcpy
import iLader.helpers.Helpers
from iLader import __version__
from iLader.usecases import Usecase

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
        self.label = "Geoprodukt importieren (iLader v" + __version__ + ")"
        self.description = "Mit diesem Tool wird ein Geoprodukt in die GeoDB importiert. Es werden nur diejenigen Geoprodukte zur Auswahl angeboten, die importierbar und dem jeweiligen PC zugewiesen sind"
        self.canRunInBackground = False
        
    def getParameterInfo(self):
        
        param1 = arcpy.Parameter(
            displayName="Import-Task",
            name="import_task",
            datatype="GPString",
            parameterType="required",
            direction="Input"
        )
        
        param1.filter.list = iLader.helpers.Helpers.get_import_tasks()
        
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
        