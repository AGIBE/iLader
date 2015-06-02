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
            
    def __replace(self, legende, sde_vektoren, sde_raster):
        self.legende = legende
        self.sde_vektoren = sde_vektoren
        self.sde_raster = sde_raster
        lyr = arcpy.mapping.Layer(self.legende)
        if lyr.supports("DATASOURCE"):
            desc = arcpy.Describe(lyr.dataSource)
            datentyp = desc.dataType
            if datentyp == "FeatureLayer": #genaue Ausgabewerte noch prüfen
                self.logger.info("Datentyp: " + datentyp)
                #TODO: lyr.replaceDataSource(sde_vektoren, "SDE_WORKSPACE", "", "false")
            elif datentyp == "RasterLayer": # genaue Ausgabewerte noch prüfen
                self.logger.info("Datentyp: " + datentyp)
                #TODO: lyr.replaceDataSource(sde_raster, "SDE_WORKSPACE", "", "false")
        lyr.save()
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus.
        Die LyrFiles und MXDs auf MosaicDatasets zeigen bereits auf ras2, alle weiteren Rasterdaten
        müssen auf ras1 zeigen.
        Vektoren zeigen auf vek1 bzw. vek3
        '''
              
        self.sde_conn_vek1_geo = self.task_config['connections']['sde_conn_vek1_geo']
        self.sde_conn_vek3_geo = self.task_config['connections']['sde_conn_vek3_geo']
        self.sde_conn_ras1_geo = self.task_config['connections']['sde_conn_ras1_geo']
        # Legenden
        self.logger.info("Legendenfiles bearbeiten")
        for legende in self.task_config["legende"]:
            self.logger.info("Legende " + legende["ziel_akt"] + " wird bearbeitet.")
            self.__replace(self, legende["ziel_akt"], self.sde_conn_vek1_geo, self.sde_conn_ras1_geo)
            self.logger.info("Legende " + legende["ziel_zs"] + " wird bearbeitet.")
            self.__replace(self, legende["ziel_zs"], self.sde_conn_vek3_geo, self.sde_conn_ras1_geo)
                    
        # MXDs
        self.logger.info("MXD-Files bearbeiten")
        for mxd in self.task_config["mxd"]:
            self.logger.info(mxd["name"] + " wird bearbeitet.")
            mxd_mapping = arcpy.mapping.MapDocument(mxd["ziel_akt"])
            lyrfiles = arcpy.mapping.ListLayers(mxd_mapping)
            for mxd_lyr in lyrfiles:
                self.__replace(self, mxd_lyr, self.sde_conn_vek1_geo, self.sde_conn_ras1_geo_geo)
                
            #TODO: umhängen für jedes lyr (funktion)
            arcpy.mapping.MapDocument(mxd["ziel_zs"])
            lyrfiles = arcpy.mapping.ListLayers(mxd_mapping)
            for mxd_lyr in lyrfiles:
                self.__replace(self, mxd_lyr, self.sde_conn_vek3_geo, self.sde_conn_ras1_geo_geo)
            mxd_mapping.save()
       
        self.finish()