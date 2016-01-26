# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import arcpy
import os

class MosaicDatasetRas2(TemplateFunction):
    '''
    Die Funktion prüft, ob in der Instanz ras2p bereits ein MosaicDataset vorhanden ist und
    erstellt es gegebenenfalls.
    Anschliessend wird das entsprechende Zeitstands.csv geladen. Vor dem Import der einzelnen
    Kacheln werden im MD bereits bestehende aktuelle Kacheln selektiert und mit BIS_JAHR und
    BIS_VERSION der neuen Version versehen.
    Am Anschluss an den Import werden Statistiken berechnet.
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["raster_ebenen"]``
    
    Nach dem Kopiervorgang setzt die Funktion auch noch die korrekten Berechtigungen d.h.
    sie vergibt SELECT-Rechte an eine Rolle. Die Rolle ist in task_config abgelegt:
    
    - ``task_config["rolle"]``

    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "MosaicDatasetRas2"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()
        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        rolle = self.task_config['rolle']
        spatial_reference = self.task_config['spatial_reference']
        sde_conn_md = self.task_config['connections']['sde_conn_ras2']
        gpr = self.task_config['gpr']
        zeitstand_jahr = self.task_config['zeitstand_jahr']
        zeitstand_version = self.task_config['zeitstand_version']
        for ebene in self.task_config['raster_ebenen']:
            source = ebene['quelle']
            target = ebene['ziel_ras2']
            md_name = ebene['gpr_ebe']
            if not arcpy.Exists(target):
                self.logger.info("Erstelle MosaicDataset für Ebene" + md_name + "...")
                arcpy.CreateMosaicDataset_management(sde_conn_md, md_name, spatial_reference, "#", "#", "NONE", "#")
                arcpy.AddField_management(target, "RASTERNAME", "text", "50")
                arcpy.AddField_management(target, "VON_JAHR", "short")
                arcpy.AddField_management(target, "VON_VERSION", "short")
                arcpy.AddField_management(target, "BIS_JAHR", "short")
                arcpy.AddField_management(target, "BIS_VERSION", "short")
                arcpy.ChangePrivileges_management(target, rolle, "GRANT")
            self.logger.info("Lade Rasterkacheln für Ebene " + md_name + "...")
            f = open(source)
            rasterList = f.readlines()
            for raster in rasterList:
                rastername = os.path.basename(raster)
                rastername = rastername.split(".")[0]
                self.logger.info("Bearbeite Raster " + rastername)
                cursor_alt = arcpy.UpdateCursor(target, "NAME = '" + rastername + "' and BIS_JAHR = 0")
                if cursor_alt:
                    try:
                        for row in cursor_alt:
                            arcpy.AddMessage("Folgende Einträge haben BIS_JAHR = 0")
                            cursor_alt_von_jahr = row.getValue("VON_JAHR")
                            arcpy.AddMessage("VON_JAHR " + unicode(cursor_alt_von_jahr))
                            cursor_alt_von_version = row.getValue("VON_VERSION")
                            arcpy.AddMessage("VON_VERSION " + unicode(cursor_alt_von_version))
                            if cursor_alt_von_jahr == int(zeitstand_jahr) and cursor_alt_von_version == int(zeitstand_version):
                                self.logger.info("Keine alte Version vorhanden.")
                            else:
                                self.logger.info("Alte Version von " + rastername + " vorhanden, wird angepasst:")
                                #~ print row.getValue("BIS_JAHR")
                                arcpy.AddMessage("BIS_JAHR neu: " + unicode(zeitstand_jahr))
                                row.setValue("BIS_JAHR", zeitstand_jahr)
                                cursor_alt.updateRow(row)
                                #~ print row.getValue("BIS_VERSION")
                                arcpy.AddMessage("BIS_VERSION neu: " + unicode(zeitstand_version))
                                row.setValue("BIS_VERSION", zeitstand_version)
                                cursor_alt.updateRow(row)
                    except Exception as e:
                        self.logger.warn("Fehler beim Erfassen der alten Zeitstände")
                        self.logger.warn(e)
                arcpy.AddMessage("Lade " + raster + "...")
                arcpy.AddRastersToMosaicDataset_management(target, "Raster Dataset", raster, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "#", "#", "#", "#", "#","#", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", "#", "#")
                arcpy.CalculateField_management(target, "RASTERNAME", """(gpr + "_" + str(!NAME!)).upper()""", "PYTHON","#")    
                cursor_neu = arcpy.UpdateCursor(target, "NAME = '" + rastername + "' and VON_JAHR is NULL")
                for row in cursor_neu:
                    arcpy.AddMessage("VON_JAHR = " + unicode(zeitstand_jahr))
                    row.setValue("VON_JAHR", zeitstand_jahr)
                    cursor_neu.updateRow(row)
                    arcpy.AddMessage("VON_VERSION = " + unicode(zeitstand_version))
                    row.setValue("VON_VERSION", zeitstand_version)
                    cursor_neu.updateRow(row)
                    arcpy.AddMessage("BIS_JAHR = 0")
                    row.setValue("BIS_JAHR", 0)
                    cursor_neu.updateRow(row)
                    arcpy.AddMessage("BIS_VERSION = 0")
                    row.setValue("BIS_VERSION", 0)
                    cursor_neu.updateRow(row)
            self.logger.info("Erstelle Statistiken für: " + target)
            arcpy.CalculateStatistics_management(target, "1", "1", "#", "OVERWRITE","Feature Set")
            self.logger.info("Statistiken sind erstellt.")            
            
            self.logger.info("Ebene " + md_name + " abgeschlossen.")    
            
        self.logger.info("Alle Ebenen wurden bearbeitet.")        
       
        self.finish()