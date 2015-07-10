# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os

class BegleitdatenReplaceSource(TemplateFunction):
    '''
    Hängt die Quelle sämtlicher Legendenfiles (.lyr) und MXD-Dateien (.mxd) auf
     die Publikationstinstanzen um. Die Files sind in task_config referenziert:
    
    - ``task_config["legende"]``
    - ``task_config["mxd"]``
    
    Umgehaengt werden muessen nur Vektordaten und ganzflaechig aktualisierte Rasterdaten.
    Begleitdaten von kachelweise aktualisierte Rasterdaten, welche in MosaicDatasets gehalten werden,
    verweisen bereits auf die korrekte Instanz, da das Lyr-Tool in der Normierung entsprechende Lyr-Files
    und mxd's bereitstellt.
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
            
    def __replace(self, legende, sde_conn_vek, sde_conn_ras, is_zeitstand, is_mxd):
        '''
        Funktion, welche die Lyrfiles und mxd auf vek2, vek3 und ras1 umhaengt.
        arcpy.replaceDataSource aendert das Schema nicht von NORM zu GEODB, wenn umgehaengt werden soll
        auch wenn die Datenquelle nicht existiert. Deshalb wird zuerst auf VEK2 umgehaengt, wo die Daten-
        quelle immer existiert. Anschliessend noch auf VEK1, worauf immer umgehaengt werden soll.
        :param legende: Ziel-Legende aus task_config (Lyr-File oder in mxd)
        :param sde_conn_vek: SDE-Connection fuer Vektordaten (VEK1 oder VEK3)
        :param sde_conn_ras: SDE-Connection fuer Rasterdaten (RAS1)
        :param is_zeitstand: Gehoert das Objekt zu einem Zeitstand? true oder false. Dieser Parameter
        steuert die Parameter der Funktion arcpy.replaceDataSource.
        :param is_mxd: Ist das Objekt ein mxd? true oder false. Dieser Parameter war nötig, weil 
        die Legendenfiles in mxd's bereits gemappt sind.
        '''
        self.legende = legende
        self.sde_conn_vek = sde_conn_vek
        self.sde_conn_ras = sde_conn_ras
        self.is_zeitstand = is_zeitstand
        self.is_mxd = is_mxd
        if self.is_mxd == "false":
            # Filter nach Lyr-Files (mxd's sind bereits mit arcpy.mapping im richtigen Datentyp)
            lyr = arcpy.mapping.Layer(self.legende)
        else:
            lyr = self.legende
        if lyr.supports("DATASOURCE") and lyr.supports("DATASETNAME"):
            gpr_ebe = lyr.datasetName
            gpr_ebe_publ = gpr_ebe.replace(self.task_config['schema']['norm'], self.task_config['schema']['geodb'])
            if self.is_zeitstand == "false":
                pass
            else:
                gpr_ebe_publ = gpr_ebe_publ + "_" + self.task_config['zeitstand']
            # lyr.dataSource gibt die sde-Connection aus, mit welche Daten geladen wurden, diese existiert nicht immer
            # deshalb wird der Pfad hier mit lyr.datasetName und der Norm-Connection gebildet
            dataSource = os.path.join(self.sde_conn_norm, lyr.datasetName)
            desc = arcpy.Describe(dataSource)
            datentyp = desc.dataType
            self.logger.info("Datentyp: " + datentyp)
            self.logger.info("Name in der Ziel-Instanz: " + gpr_ebe_publ)           
            if datentyp == "FeatureClass":
                try:
                    self.logger.info('Haenge Quelle nach ' + self.sde_conn_vek + ' um.')
                    # Kniff: zuerst auf vek2 umhängen, wo die Quelle existiert (wenn Parameter=False wird Schema GEODB nicht übernommmen.)
                    lyr.replaceDataSource(self.sde_conn_vek, "SDE_WORKSPACE", gpr_ebe_publ, True)
                    if self.is_mxd == "false":
                        if self.is_zeitstand == "true":
                            lyr.saveACopy(legende["ziel_zs"], "10.0")
                    if self.is_zeitstand == "false":
                        # Filter, damit nur die aktuellen Zeitstände nach auch noch auf vek1 umgehängt werden
                        self.logger.info('Haenge Quelle nach ' + self.sde_conn_vek1_geo +' um.')
                        lyr.replaceDataSource(self.sde_conn_vek1_geo, "SDE_WORKSPACE", gpr_ebe_publ, False)
                        if self.is_mxd == "false":
                            lyr.saveACopy(legende["ziel_akt"], "10.0")
                    if self.is_mxd == "false" and self.is_zeitstand == "true":
                        self.logger.info("Fuege der Bezeichnung den Zeitstand an.")
                        lyr_bezeichnung = lyr.name
                        lyr_bezeichnung_zs = lyr_bezeichnung + ", " + self.task_config['zeitstand']
                        lyr.name = lyr_bezeichnung_zs
                        lyr.save()
                except Exception as e:
                    self.logger.warn('FEHLER: Die Datenquelle konnte nicht umgehaengt werden!')
                    self.logger.warn(e)
                if self.is_mxd == "false":
                    lyr.save()    
            elif datentyp == "RasterDataset":
                try:
                    self.logger.info("Haenge Quelle nach " + self.sde_conn_ras + " um.")
                    lyr.replaceDataSource(self.sde_conn_ras, "SDE_WORKSPACE", gpr_ebe_publ, True)
                    if self.is_mxd == "false":
                        if self.is_zeitstand == "false":
                            lyr.saveACopy(legende["ziel_akt"], "v10.0")
                        if self.is_zeitstand == "true":
                            self.logger.info("Fuege der Bezeichnung den Zeitstand an.")
                            lyr_bezeichnung = lyr.name
                            lyr_bezeichnung_zs = lyr_bezeichnung + ", " + self.task_config['zeitstand']
                            lyr.name = lyr_bezeichnung_zs
                            lyr.saveACopy(legende["ziel_zs"], "v10.0")
                except Exception as e:
                    self.logger.warn("FEHLER: Die Datenquelle konnte nicht umgehaengt werden!")
                    self.logger.warn(e)

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus.
        Die LyrFiles und MXDs auf MosaicDatasets zeigen bereits auf ras2, alle weiteren Rasterdaten
        müssen auf ras1 zeigen.
        Vektoren zeigen auf vek1 bzw. vek3
        '''
              
        self.sde_conn_vek1_geo = self.task_config['connections']['sde_conn_vek1_geo']
        self.sde_conn_vek2_geo = self.task_config['connections']['sde_conn_vek2_geo']
        self.sde_conn_vek3_geo = self.task_config['connections']['sde_conn_vek3_geo']
        self.sde_conn_ras1_geo = self.task_config['connections']['sde_conn_ras1_geo']
        self.sde_conn_norm = self.task_config['connections']['sde_conn_norm']
        # Legenden
        self.logger.info("Legendenfiles bearbeiten")
        for legende in self.task_config["legende"]:
            self.logger.info("Legende " + legende["quelle"] + " wird bearbeitet.")
            self.__replace(legende["quelle"], self.sde_conn_vek2_geo, self.sde_conn_ras1_geo, "false", "false")
            self.logger.info("Legende " + legende["quelle"] + " wird bearbeitet.")
            self.__replace(legende["quelle"], self.sde_conn_vek3_geo, self.sde_conn_ras1_geo, "true", "false")   
        self.logger.info("alle Legendenfiles sind umgehängt.")
        
        # MXDs
        self.logger.info("MXD-Files bearbeiten")
        for mxd in self.task_config["mxd"]:
            self.logger.info(mxd["quelle"] + " wird bearbeitet.")
            mxd_mapping = arcpy.mapping.MapDocument(mxd["quelle"])
            lyrfiles = arcpy.mapping.ListLayers(mxd_mapping)
            for lyr in lyrfiles:
                # lyrname = (lyr.name).encode('utf-8')
                self.lyr = lyr
                self.__replace(self.lyr, self.sde_conn_vek2_geo, self.sde_conn_ras1_geo, "false", "true")
            mxd_mapping.saveACopy(mxd["ziel_akt"], "10.0")
            self.logger.info(mxd["quelle"] + " wird bearbeitet.")    
            mxd_mapping = arcpy.mapping.MapDocument(mxd["quelle"])
            lyrfiles = arcpy.mapping.ListLayers(mxd_mapping)
            for lyr in lyrfiles:
                # lyrname = (lyr.name).encode('utf-8')
                self.lyr = lyr
                self.__replace(self.lyr, self.sde_conn_vek3_geo, self.sde_conn_ras1_geo, "true", "true")
            mxd_mapping.save(mxd["ziel_zs"], "10.0")
        self.logger.info("alle MXD-Files sind umgehängt.")    
       
        self.finish()