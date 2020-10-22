# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os
import shutil

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

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "BegleitdatenReplaceSource"
        TemplateFunction.__init__(self, task_config, general_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
            
    def __replace(self, legende, sde_conn_vek, sde_conn_ras, sde_conn_norm, is_zeitstand, is_mxd):
        '''
        Funktion, welche die Lyrfiles und mxd auf vek2, vek3 und ras1 umhaengt.
        arcpy.replaceDataSource aendert das Schema nicht von NORM zu GEODB, wenn umgehaengt werden soll
        auch wenn die Datenquelle nicht existiert. Deshalb wird zuerst auf VEK2 umgehaengt, wo die Daten-
        quelle immer existiert. Anschliessend noch auf VEK1, worauf immer umgehaengt werden soll.
        TODO: Funktion kann eventuell durch die AGILib abgelöst werden.
        :param legende: Ziel-Legende aus task_config (Lyr-File oder in mxd)
        :param sde_conn_vek: SDE-Connection fuer Vektordaten (VEK1 oder VEK3)
        :param sde_conn_ras: SDE-Connection fuer Rasterdaten (RAS1)
        :param sde_conn_norm: SDE-Connection fuer Vektordaten (TEAM)
        :param is_zeitstand: Gehoert das Objekt zu einem Zeitstand? true oder false. Dieser Parameter
        steuert die Parameter der Funktion arcpy.replaceDataSource.
        :param is_mxd: Ist das Objekt ein mxd? true oder false. Dieser Parameter war noetig, weil 
        die Legendenfiles in mxd's bereits gemappt sind.
        '''
        legende = legende
        sde_conn_vek = sde_conn_vek
        sde_conn_ras = sde_conn_ras
        is_zeitstand = is_zeitstand
        is_mxd = is_mxd
        if not is_mxd:
            # Filter nach Lyr-Files (mxd's sind bereits mit arcpy.mapping im richtigen Datentyp)
            lyr = arcpy.mapping.Layer(legende)
        else:
            lyr = legende
        change_src = True
        if lyr.supports("SERVICEPROPERTIES"):
            if ('ras2' in lyr.serviceProperties.get('Server') or lyr.isServiceLayer):
                # Ist es MosaicDataset? Dann müssen Datenquellen nicht umgehängt werden
                # Ist es eine Cache-Ebene? Dann müssen Datenquellen nicht umgehängt werden
                change_src = False
        if lyr.supports("DATASOURCE") and lyr.supports("DATASETNAME") and change_src:
            gpr_ebe = lyr.datasetName
            gpr_ebe_publ = gpr_ebe.replace(self.task_config['schema']['norm'], self.task_config['schema']['geodb'])
            if is_zeitstand:
                gpr_ebe_publ = gpr_ebe_publ + "_" + self.task_config['zeitstand']
            # lyr.dataSource gibt die sde-Connection aus, mit welche Daten geladen wurden, diese existiert nicht immer
            # deshalb wird der Pfad hier mit lyr.datasetName und der Norm-Connection gebildet
            dataSource = os.path.join(sde_conn_norm, lyr.datasetName)
            if arcpy.Exists(dataSource):
                desc = arcpy.Describe(dataSource)
                datentyp = desc.dataType
                self.logger.info("Datentyp: " + datentyp)
                self.logger.info("Name in der Ziel-Instanz: " + gpr_ebe_publ)           
                if datentyp == "FeatureClass":
                    try:
                        self.logger.info('Haenge Quelle nach ' + sde_conn_vek + ' um.')
                        # Kniff: zuerst auf vek2 umhängen, wo die Quelle existiert (wenn Parameter=False wird Schema GEODB nicht ??nommmen.)
                        lyr.replaceDataSource(sde_conn_vek, "SDE_WORKSPACE", gpr_ebe_publ, True)
                        if not is_mxd:
                            lyr.save()
                        if not is_zeitstand:
                            # Filter, damit nur die aktuellen Zeitst寤e nach auch noch auf vek1 umgeh寧t werden
                            self.logger.info('Haenge Quelle nach ' + self.sde_conn_vek1_geo +' um.')
                            lyr.replaceDataSource(self.sde_conn_vek1_geo, "SDE_WORKSPACE", gpr_ebe_publ, False)
                            if not is_mxd:
                                lyr.save()
                        if not is_mxd and is_zeitstand:
                            self.logger.info("Fuege der Bezeichnung den Zeitstand an.")
                            lyr_bezeichnung = lyr.name
                            lyr_bezeichnung_zs = lyr_bezeichnung + ", " + self.task_config['zeitstand']
                            lyr.name = lyr_bezeichnung_zs
                            lyr.save()
                    except Exception as e:
                        self.logger.warn('FEHLER: Die Datenquelle konnte nicht umgehaengt werden!')
                        self.logger.warn(e)
                    if not is_mxd:
                        lyr.save()    
                elif datentyp == "RasterDataset":
                    try:
                        self.logger.info("Haenge Quelle nach " + sde_conn_ras + " um.")
                        # Parameter auf False gesetzt, da z.T. unexpected error (verm. weil Raster und nicht DC auf workp...
                        lyr.replaceDataSource(sde_conn_ras, "SDE_WORKSPACE", gpr_ebe_publ, False)
                        if not is_mxd:
                            lyr.save()
                            if is_zeitstand:
                                self.logger.info("Fuege der Bezeichnung den Zeitstand an.")
                                lyr_bezeichnung = lyr.name
                                lyr_bezeichnung_zs = lyr_bezeichnung + ", " + self.task_config['zeitstand']
                                lyr.name = lyr_bezeichnung_zs
                                lyr.save()
                    except Exception as e:
                        self.logger.warn("FEHLER: Die Datenquelle konnte nicht umgehaengt werden!")
                        self.logger.warn(e)
            else:
                self.logger.warn("Datenquelle nicht in der Instanz " + sde_conn_norm)
                self.logger.warn("Die Quelle kann nicht umgehängt werden.")
        else:
            self.logger.info("Es handelt sich um ein MosaicDataset oder einen Cache-Dienst. Datenquelle muss nicht umgehängt werden.")

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
            self.logger.info("Legende %s wird bearbeitet." % (legende["ziel_akt"]))
            self.__replace(legende["ziel_akt"], self.sde_conn_vek2_geo, self.sde_conn_ras1_geo, self.sde_conn_norm, False, False)
            self.logger.info("Legende %s wird bearbeitet." % (legende["ziel_zs"]))
            self.__replace(legende["ziel_zs"], self.sde_conn_vek3_geo, self.sde_conn_ras1_geo, self.sde_conn_norm, True, False)   
        self.logger.info("alle Legendenfiles sind umgehängt.")
        
        # Temporäre Raster-lyr-Files löschen
        self.logger.info("Temporäre lyr-Files von Rasterdatasets löschen (falls vorhanden)")
        for f in os.listdir(self.task_config['ziel']['ziel_begleitdaten_symbol']):
            if f.upper().startswith("DELETE_"):
                self.logger.info("Temporäres lyr-File %s wird gelöscht." % (f))
                os.remove(os.path.join(self.task_config['ziel']['ziel_begleitdaten_symbol'],f))
        
        # MXDs
        self.logger.info("MXD-Files bearbeiten")
        for mxd in self.task_config["mxd"]:
            self.logger.info("%s wird bearbeitet." % (mxd["ziel_akt"]))
            mxd_mapping = arcpy.mapping.MapDocument(mxd["ziel_akt"])
            lyrfiles = arcpy.mapping.ListLayers(mxd_mapping)
            for lyr in lyrfiles:
                self.lyr = lyr
                self.__replace(self.lyr, self.sde_conn_vek2_geo, self.sde_conn_ras1_geo, self.sde_conn_norm, False, True)
            mxd_mapping.save()
            self.logger.info("%s wird bearbeitet." % (mxd["ziel_zs"]))    
            mxd_mapping = arcpy.mapping.MapDocument(mxd["ziel_zs"])
            lyrfiles = arcpy.mapping.ListLayers(mxd_mapping)
            for lyr in lyrfiles:
                self.lyr = lyr
                self.__replace(self.lyr, self.sde_conn_vek3_geo, self.sde_conn_ras1_geo, self.sde_conn_norm, True, True)
            mxd_mapping.save()
        self.logger.info("alle MXD-Files sind umgehängt.")       
       
        self.finish()