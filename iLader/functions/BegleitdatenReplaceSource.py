# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy

class BegleitdatenReplaceSource(TemplateFunction):
    '''
    Hängt die Quelle sämtlicher Legendenfiles (.lyr) und MXD-Dateien (.mxd) auf den
    die Publikationstinstanzen um. Die Files sind in task_config referenziert:
    
    - ``task_config["legende"]``
    - ``task_config["mxd"]``
    '''

    def __init__(self, logger, task_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"BegleitdatenReplaceSource"
        TemplateFunction.__init__(self, logger, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info(u"Funktion " + self.name + u" wird ausgelassen.")
        else:
            self.logger.info(u"Funktion " + self.name + u" wird ausgeführt.")
            self.start()
            self.__execute()
            
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus.
        Die LyrFiles und MXDs auf MosaicDatasets zeigen bereits auf ras2, alle weiteren Rasterdaten
        müssen auf ras1 zeigen.
        Vektoren zeigen auf vek1 bzw. vek3
        '''
        # Legenden
        self.logger.info("Legendenfiles bearbeitet")
        for legende in self.task_config["legende"]:
            self.logger.info("Legende " + legende["ziel_akt"] + " wird bearbeitet.")
            lyr = arcpy.mapping.Layer(legende["ziel_akt"])
            desc = arcpy.Describe(lyr)
            datentyp = desc.dataType
            if datentyp == "FeatureLayer":
                self.logger.info("Datentyp: " + datentyp)
                #TODO: lyr.replaceDataSource(geo_vek1, "SDE_WORKSPACE", "", "false")
            self.logger.info("Legende " + legende["ziel_zs"] + " wird bearbeitet.")
            lyr = arcpy.mapping.Layer(legende["ziel_zs"])
            desc = arcpy.Describe(lyr)
            datentyp = desc.dataType
            if datentyp == "FeatureLayer":
                self.logger.info("Datentyp: " + datentyp)
                #TODO: lyr.replaceDataSource(workspace_path, workspace_type, dataset_name, validate)
        
        # MXDs
        self.logger.info("MXD-Files auslesen")
        for mxd in self.task_config["mxd"]:
            self.logger.info(mxd["name"] + " wird bearbeitet.")
            arcpy.mapping.MapDocument(mxd["ziel_akt"])
            #TODO: umhängen für jedes lyr (funktion)
            arcpy.mapping.MapDocument(mxd["ziel_zs"])
        
       
        self.finish()