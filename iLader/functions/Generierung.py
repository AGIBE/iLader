# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import os
import json
import cx_Oracle as ora
from iLader.helpers.Crypter import Crypter

class Generierung(TemplateFunction):
    '''
    Sammelt sämtliche benötigten Informationen zusammen aus:
    - DataDictionary
    - General Config
    - GeoDBProzess
    - ÖREB-Kataster
    Die Informationen werden in die task_config geschrieben.
    '''
# TODO: Parameter einfügen für task_config: bestehende Daten überschreiben, per Default = JA
# Parameter kann in task_config manuell angepasst werden, falls doch mal nicht überschrieben werdeK:\Anwend\GeoDB\P3_Applikation\Neukonzeption\Importn soll
# z.B. bei grossen Rasterdaten

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "Generierung"
        TemplateFunction.__init__(self, task_config)

        self.task_config = task_config
        self.general_config = general_config

        # Wenn die JSON-Datei existiert und der Parameter task_config_load_from_JSON True ist,
        # wird die Task-Config aus der JSON-Datei geladen. In diesem Fall wird die eigentliche
        # Generierungsfunktion nicht ausgeführt.
        if os.path.exists(self.task_config['task_config_file']) and self.task_config['task_config_load_from_JSON']:
            self.__load_task_config()
            # Dieser Wert muss explizit auf True gesetzt werden, da er im JSON-File
            # auch auf False sein könnte.
            self.task_config['task_config_load_from_JSON'] = True
            self.finish()
        else:
            self.__execute()

    def __db_connect(self, instance, usergroup, sql_name):
        #TODO: Parameter einführen (true, false) für fetchall bzw. fetchone; anschliessend ausführen
        self.sql_name = sql_name
        self.instance = instance
        self.usergroup = usergroup
        self.username = self.general_config['users'][self.usergroup]['username']
        self.password = self.general_config['users'][self.usergroup]['password']
        self.db = self.general_config['instances'][self.instance]
        self.logger.info("Username: " + self.username)
        self.logger.info("Verbindung herstellen mit der Instanz " + self.db)
        self.connection = ora.connect(self.username, self.password, self.db)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.sql_name)
        self.result = self.cursor.fetchall()
        self.connection.close()    
    
    def __get_importe_dd(self):
        self.task_id = unicode(self.task_config['task_id'])
        self.logger.info(self.task_id)
        self.sql_dd_importe = "select a.gzs_objectid from geodb_dd.tb_task a where a.task_objectid = '" + self.task_id + "'"
        self.__db_connect('team', 'geodb_dd', self.sql_dd_importe)
        for row in self.result:
            self.gzs_objectid = unicode(row[0])

    
    def __get_gpr_info(self):
        '''
        Diese Funktion sucht die Informationen auf Stufe Geoprodukt aus dem DD der GeoDB
        und aus GeoDBprozess zusammen
        DD GeoDB: Geoproduktcode, Jahr, Version
        GeoDBprozess: Rolle, sofern eine definiert ist, ansonsten Standardrolle
        '''
        self.sql_dd_gpr = "SELECT a.gpr_bezeichnung, b.gzs_jahr, b.gzs_version, a.gpr_viewer_freigabe from geodb_dd.tb_geoprodukt_zeitstand b join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"
        self.__db_connect('team', 'geodb_dd', self.sql_dd_gpr)
        for row in self.result:
            self.gpr = row[0].decode('cp1252')
            self.jahr = unicode(row[1]).decode('cp1252')
            self.version = unicode(row[2]).decode('cp1252')
            self.version = self.version.zfill(2)
            self.zeitstand = self.jahr + "_" + self.version        
        self.sql_gpr_role = "SELECT a.db_rollen from gdbp.geoprodukte a where a.code = '" + self.gpr + "'"
        self.__db_connect('work', 'gdbp', self.sql_gpr_role)
        for row in self.result:
            if row[0]:
                self.gpr_role_gdbp = row[0].decode('cp1252')
                self.rolle_freigabe = self.gpr_role_gdbp
            else:
                self.rolle_freigabe = self.general_config['standard_rolle']
        self.default_tolerance = self.general_config['default_tolerance']  
        self.default_resolution = self.general_config['default_resolution']
        self.spatial_reference = self.general_config['spatial_reference']
       
    
    def __get_ebe_dd(self):
        self.sql_dd_ebe = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, g.dat_bezeichnung_de from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"   
        self.__db_connect('team', 'geodb_dd', self.sql_dd_ebe)
        for row in self.result:
            self.logger.info(row)
            ebeVecDict = {}
            ebeRasDict = {}
            gpr = row[0].decode('cp1252')
            ebe = row[1].decode('cp1252')
            jahr = unicode(row[2]).decode('cp1252')
            version = unicode(row[3]).decode('cp1252')
            version = version.zfill(2)
            datentyp = row[4].decode('cp1252')            
            zeitstand = jahr + "_" + version
            gpr_ebe = unicode(gpr) + "_" + unicode(ebe)
            quelle_schema_gpr_ebe = self.schema_norm + "." + gpr_ebe
            quelle = os.path.join(self.sde_conn_norm, quelle_schema_gpr_ebe)
            ziel_schema_gpr_ebe = self.schema_geodb + "." + gpr_ebe
            ziel_schema_gpr_ebe_zs = ziel_schema_gpr_ebe + "_" + zeitstand     
            ziel_vek1 = os.path.join(self.sde_conn_vek1, ziel_schema_gpr_ebe)
            ziel_vek2 = os.path.join(self.sde_conn_vek2, ziel_schema_gpr_ebe)
            ziel_vek3 = os.path.join(self.sde_conn_vek3, ziel_schema_gpr_ebe_zs)
            ziel_ras1_akt = os.path.join(self.sde_conn_ras1, ziel_schema_gpr_ebe) 
            ziel_ras1_zs = os.path.join(self.sde_conn_ras1, ziel_schema_gpr_ebe_zs)
            ziel_ras2 = os.path.join(self.sde_conn_ras2, ziel_schema_gpr_ebe)
            if datentyp != 'Rastermosaik' and datentyp != 'Rasterkatalog' and datentyp != 'Mosaicdataset':
                self.sql_ind_gdbp = "SELECT b.felder, b." + '"unique"' + " from gdbp.index_attribut b join gdbp.geoprodukte a on b.id_geoprodukt = a.id_geoprodukt where a.code = '" + gpr + "' and b.ebene = '" + ebe + "'"
                self.__db_connect('work', 'gdbp', self.sql_ind_gdbp)
                self.indList = []
                for row in self.result:
                    indDict = {}
                    ind_attr = row[0].decode('cp1252')
                    indextyp = unicode(row[1]).decode('cp1252')
                    if indextyp == "1":
                        ind_unique = "True"
                    elif indextyp == "2":
                        ind_unique = "False"
                    indDict['attribute'] = ind_attr
                    indDict['unique'] = ind_unique            
                    self.indList.append(indDict)
                ebeVecDict['indices'] = self.indList
                ebeVecDict['datentyp']= datentyp
                ebeVecDict['gpr_ebe'] = gpr_ebe
                ebeVecDict['quelle'] = quelle
                ebeVecDict['ziel_vek1'] = ziel_vek1
                ebeVecDict['ziel_vek2'] = ziel_vek2
                ebeVecDict['ziel_vek3'] = ziel_vek3
                self.ebeVecList.append(ebeVecDict)            
            elif datentyp == 'Rastermosaik': #TODO: ev. später Rasterdataset
                ebeRasDict['datentyp'] = datentyp
                ebeRasDict['gpr_ebe'] = gpr_ebe
                ebeRasDict['quelle'] = quelle
                ebeRasDict['ziel_ras1']= ziel_ras1_akt
                ebeRasDict['ziel_ras1_zs']= ziel_ras1_zs
                self.ebeRasList.append(ebeRasDict)
#             elif datentyp == 'Rasterkatalog' or datentyp == 'Mosaicdataset':
#                 ebeRasDict['datentyp'] = datentyp
#                 ebeRasDict['gpr_ebe'] = gpr_ebe
#                 rasterkacheln_pfad = os.path.join(self.general_config['quelle_begleitdaten'], gpr, self.general_config['quelle_begleitdaten_work'], self.general_config['raster']['quelle_rasterkacheln'], self.general_config['raster']['historisch'])
#                 rasterkacheln_csv = gpr_ebe + "_" + zeitstand + ".csv"
#                 ebeRasDict['quelle'] = os.path.join(rasterkacheln_pfad, rasterkacheln_csv)
#                 ebeRasDict['ziel_ras2'] = ziel_ras2
#                 self.ebeRasList.append(ebeRasDict)          
                         
                
    def __get_leg_dd(self):
        '''
        Diese Funktion definiert die Legendenfiles für alle Ebenen gemäss den Einträgen im DataDictionary
        Die Bezeichnung eines Legendenfiles setzt sich normalerweise zusammen aus:
        - Geoproduktcode
        - Ebenencode
        - Legendencode
        - Sprachkürzel
        
        Eine Ausnahme bilden die Legendenfiles von MosaicDatasets. Diese beinhalten zusätzlich die Information zum Zeitstand (Jahr_Version).
        Aus zwei Gründen zeigen sie ausserdem bereits auf die Publikationsinstanzen:
        - der Import der Rasterkacheln erfolgt direkt nach RAS2P (Effizienz) 
        - ein Umhängen der Datenquelle von MosaicDatasets lässt diese ihre Symbolisierungsinformationen verschwinden
        '''
        self.sql_dd_ebe = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, f.leg_bezeichnung, h.spr_kuerzel, g.dat_objectid from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid JOIN geodb_dd.tb_legende f on f.ezs_objectid = d.ezs_objectid JOIN geodb_dd.tb_sprache h on h.spr_objectid = f.spr_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"   
        self.__db_connect('team', 'geodb_dd', self.sql_dd_ebe)
        for row in self.result:
            self.legDict = {}
            self.logger.info('Legendendetails')
            self.logger.info(row)
            self.gpr = row[0].decode('cp1252')
            self.ebe = row[1].decode('cp1252')
            self.jahr = unicode(row[2])
            self.version = unicode(row[3])
            self.version = self.version.zfill(2)           
            self.zeitstand = self.jahr + "_" + self.version
            self.leg = row[4].decode('cp1252')
            self.spr = row[5].decode('cp1252')
            self.datentyp = row[6]
            self.symbol_name = self.gpr + "_" + self.ebe + "_" + self.leg + "_" + self.spr + ".lyr"
            self.symbol_name_akt = "AKTUELL_" + self.gpr + "_" + self.ebe + "_" + self.leg + "_" + self.spr + ".lyr"
            self.symbol_name_zs = self.gpr + "_" + self.ebe + "_" + self.zeitstand + "_" + self.leg + "_" + self.spr + ".lyr"
            self.logger.info(self.symbol_name)
            self.quelle_symbol =  os.path.join(self.quelle_begleitdaten_symbol, self.symbol_name)
            self.ziel_symbol_akt = os.path.join(self.ziel_begleitdaten_symbol, self.symbol_name_akt)
            self.ziel_symbol_zs = os.path.join(self.ziel_begleitdaten_symbol, self.symbol_name_zs)
            self.legDict['name'] = self.symbol_name.lower()
            self.legDict['quelle'] = self.quelle_symbol.lower()
            self.legDict['ziel_akt'] = self.ziel_symbol_akt.upper()
            self.legDict['ziel_zs'] = self.ziel_symbol_zs.upper()
            self.legList.append(self.legDict)
            if self.datentyp == 9:
                self.symbol_name = self.gpr + "_" + self.ebe + "_" + self.zeitstand + "_" + self.leg + "_" + self.spr + ".lyr"
                self.symbol_name_zs = self.gpr + "_" + self.ebe + "_" + self.zeitstand + "_" + self.leg + "_" + self.spr + ".lyr"
                self.symbol_name_akt = "DELETE_" + self.gpr + "_" + self.ebe + "_" + self.leg + "_" + self.spr + ".lyr"
                self.legDict['name'] = self.symbol_name.lower()
                self.quelle_symbol =  os.path.join(self.quelle_begleitdaten_symbol, self.symbol_name)
                self.ziel_symbol_akt = os.path.join(self.ziel_begleitdaten_symbol, self.symbol_name_akt)
                self.ziel_symbol_zs = os.path.join(self.ziel_begleitdaten_symbol, self.symbol_name_zs)
                self.legDict['quelle'] = self.quelle_symbol.lower()
                self.legDict['ziel_akt'] = self.ziel_symbol_akt.upper()
                self.legDict['ziel_zs'] = self.ziel_symbol_zs.upper()

    
    def __get_mxd_dd(self, lang):
            self.mxdDict = {}
            self.lang = lang
            self.mxd_lang = self.gpr + "_" + self.lang + ".mxd"
            self.quelle_mxd_lang = os.path.join(self.quelle_begleitdaten_mxd, self.mxd_lang)
            self.mxd_lang_akt = "AKTUELL_" + self.gpr + "_" + self.gpr + "_" + self.lang + ".mxd"
            self.ziel_mxd_lang_akt = os.path.join(self.ziel_begleitdaten_mxd, self.mxd_lang_akt)
            self.mxd_lang_zs = self.gpr + "_" + self.zeitstand + "_" + self.gpr + "_" + self.lang + ".mxd"
            self.ziel_mxd_lang_zs = os.path.join(self.ziel_begleitdaten_mxd, self.mxd_lang_zs)
            self.mxdDict['name'] = self.mxd_lang
            self.mxdDict['quelle'] = self.quelle_mxd_lang
            self.mxdDict['ziel_akt'] = self.ziel_mxd_lang_akt.upper()
            self.mxdDict['ziel_zs'] = self.ziel_mxd_lang_zs.upper()             
            self.mxdList.append(self.mxdDict)
    
    def __get_fak_begleitdaten(self):
        for root, dirs, files in os.walk(self.quelle_begleitdaten_symbol):
            self.logger.info("Liste Files auf:")
            for file in files:
                styleDict = {}
                fontDict = {}
                if file.endswith('.STYLE') or file.endswith('.style'):
                    styleDict['name'] = file
                    styleDict['quelle'] = os.path.join(self.quelle_begleitdaten_symbol, file)
                    self.style_ziel_akt = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + file)
                    styleDict['ziel_akt'] = self.style_ziel_akt.upper()
                    self.style_zs = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + self.zeitstand + "_" + file)
                    styleDict['ziel_zs'] = self.style_zs.upper()
                    self.styleList.append(styleDict)
                elif file.endswith('.ttf') or file.endswith('.TTF'):
                    fontDict['name'] = file
                    fontDict['quelle'] = os.path.join(self.quelle_begleitdaten_symbol, file)
                    self.font_akt = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + file)
                    fontDict['ziel_akt'] = self.font_akt.upper()
                    self.font_zs = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + self.zeitstand + "_" + file)
                    fontDict['ziel_zs'] = self.font_zs.upper()
                    self.fontList.append(fontDict)
            for dir in dirs:
                zusatzDict = {}
                if dir == "zusatzdaten":
                    zusatzDict['quelle'] = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_zusatzdaten'])
                    zusatzDict['ziel'] = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_zusatzdaten'])
                    self.zusatzList.append(zusatzDict)         

    def __define_quelle_ziel_begleitdaten(self):
            self.zielDict = {}
            self.quelle_begleitdaten_gpr = os.path.join(self.general_config['quelle_begleitdaten'], self.gpr, self.general_config['quelle_begleitdaten_work'])
            self.quelle_begleitdaten_mxd = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_mxd'])
            self.quelle_begleitdaten_symbol = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_symbol'])
            self.quelle_begleitdaten_zusatzdaten = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_zusatzdaten'])
            self.ziel_begleitdaten_gpr = os.path.join(self.general_config['ziel_begleitdaten'], self.gpr)
            self.ziel_begleitdaten_mxd = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_mxd'])
            self.ziel_begleitdaten_symbol = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_symbol'])
            self.ziel_begleitdaten_zusatzdaten = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_zusatzdaten'])
            self.zielDict['ziel_begleitdaten_gpr'] = self.ziel_begleitdaten_gpr
            self.zielDict['ziel_begleitdaten_mxd'] = self.ziel_begleitdaten_mxd
            self.zielDict['ziel_begleitdaten_symbol'] = self.ziel_begleitdaten_symbol
            self.zielDict['ziel_begleitdaten_zusatzdaten'] = self.ziel_begleitdaten_zusatzdaten
      
         
    def __get_wtb_dd(self):
        self.sql_dd_wtb = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, e.wtb_bezeichnung from geodb_dd.tb_wertetabelle e join geodb_dd.tb_ebene_zeitstand d on e.ezs_objectid = d.ezs_objectid join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"
        self.__db_connect('team', 'geodb_dd', self.sql_dd_wtb)
        for row in self.result:
            wtbDict = {}
            self.logger.info(row)
            gpr = row[0].decode('cp1252')
            self.logger.info(type(gpr))
            wtb = row[4].decode('cp1252')
            jahr = unicode(row[2]).decode('cp1252')
            version = unicode(row[3]).decode('cp1252')
            version = version.zfill(2)
            zeitstand = jahr + "_" + version
            gpr_wtb = unicode(gpr) + "_" + unicode(wtb)            
            quelle_schema_gpr_wtb = self.schema_norm + "." + gpr_wtb
            quelle = os.path.join(self.sde_conn_norm, quelle_schema_gpr_wtb)
            ziel_schema_gpr_wtb = self.schema_geodb + "." + gpr_wtb
            ziel_schema_gpr_wtb_zs = ziel_schema_gpr_wtb + "_" + zeitstand                
            ziel_vek1 = os.path.join(self.sde_conn_vek1, ziel_schema_gpr_wtb)
            ziel_vek2 = os.path.join(self.sde_conn_vek2, ziel_schema_gpr_wtb)
            ziel_vek3 = os.path.join(self.sde_conn_vek3, ziel_schema_gpr_wtb_zs)
            
            self.sql_ind_gdbp = "SELECT b.felder, b." + '"unique"' + " from gdbp.index_attribut b join gdbp.geoprodukte a on b.id_geoprodukt = a.id_geoprodukt where a.code = '" + gpr + "' and b.ebene = '" + wtb + "'"
            self.__db_connect('work', 'gdbp', self.sql_ind_gdbp)
            self.indList = []
            for row in self.result:
                indDict = {}
                ind_attr = row[0].decode('cp1252')
                indextyp = unicode(row[1]).decode('cp1252')
                if indextyp == "1":
                    ind_unique = "True"
                elif indextyp == "2":
                    ind_unique = "False"
                indDict['attribute'] = ind_attr
                indDict['unique'] = ind_unique            
                self.indList.append(indDict)
            wtbDict['indices'] = self.indList
            wtbDict['datentyp']= "Tabelle"
            wtbDict['gpr_ebe'] = gpr_wtb
            wtbDict['quelle'] = quelle
            wtbDict['ziel_vek1'] = ziel_vek1
            wtbDict['ziel_vek2'] = ziel_vek2
            wtbDict['ziel_vek3'] = ziel_vek3
            self.ebeVecList.append(wtbDict)
               
    def __define_qs(self):
        self.qsDict = {}
        #TODO: self.sql_dd_importe = "select * from geodb_dd.tb_importe_geodb"
        #TODO: self.__db_connect('dd_connection', self.sql_dd_importe)
        #TODO: dma_erlaubt für qs auslesen und 'dma_erlaubt' übergeben
        self.qsDict['dma_erlaubt'] = 'false'
        self.qsDict['checkskript_passed'] = 'undefined'
        self.qsDict['deltachecker_passed'] = 'undefined'
        self.qsDict['qa_framework_passed'] = 'undefined'
        self.qsDict['qs_gesamt_passed'] = 'undefined'
        
  
        
    def __define_connections(self):
        self.connDict = {}
        self.config_secret = os.environ['GEODBIMPORTSECRET']
        self.sde_connection_directory = os.path.join(self.config_secret, 'connections')
        self.sde_conn_team_dd = os.path.join(self.sde_connection_directory, 'team_dd.sde')
        self.sde_conn_vek1 = os.path.join(self.sde_connection_directory, 'vek1.sde')
        self.sde_conn_vek2 = os.path.join(self.sde_connection_directory, 'vek2.sde')
        self.sde_conn_vek3 = os.path.join(self.sde_connection_directory, 'vek3.sde')
        self.sde_conn_ras1 = os.path.join(self.sde_connection_directory, 'ras1.sde')
        self.sde_conn_ras2 = os.path.join(self.sde_connection_directory, 'ras2.sde')
        self.sde_conn_norm = os.path.join(self.sde_connection_directory, 'norm.sde')
        self.sde_conn_vek1_geo = os.path.join(self.sde_connection_directory, 'vek1_geo.sde')
        self.sde_conn_vek2_geo = os.path.join(self.sde_connection_directory, 'vek2_geo.sde')
        self.sde_conn_vek3_geo = os.path.join(self.sde_connection_directory, 'vek3_geo.sde')
        self.sde_conn_ras1_geo = os.path.join(self.sde_connection_directory, 'ras1_geo.sde')        
        self.sde_conn_team_oereb = os.path.join(self.sde_connection_directory, 'team_oereb.sde')
        self.sde_conn_vek1_oereb = os.path.join(self.sde_connection_directory, 'vek1_oereb.sde')
        self.sde_conn_vek2_oereb = os.path.join(self.sde_connection_directory, 'vek2_oereb.sde')      
        self.sde_conn_team_oereb2 = os.path.join(self.sde_connection_directory, 'team_oereb2.sde')
        self.sde_conn_vek1_oereb2 = os.path.join(self.sde_connection_directory, 'vek1_oereb2.sde')
        self.sde_conn_vek2_oereb2 = os.path.join(self.sde_connection_directory, 'vek2_oereb2.sde')
        self.connDict['sde_conn_team_dd'] = self.sde_conn_team_dd
        self.connDict['sde_conn_vek1'] = self.sde_conn_vek1
        self.connDict['sde_conn_vek2'] = self.sde_conn_vek2
        self.connDict['sde_conn_vek3'] = self.sde_conn_vek3
        self.connDict['sde_conn_ras1'] = self.sde_conn_ras1
        self.connDict['sde_conn_ras2'] = self.sde_conn_ras2
        self.connDict['sde_conn_norm'] = self.sde_conn_norm
        self.connDict['sde_conn_vek1_geo'] = self.sde_conn_vek1_geo
        self.connDict['sde_conn_vek2_geo'] = self.sde_conn_vek2_geo
        self.connDict['sde_conn_vek3_geo'] = self.sde_conn_vek3_geo
        self.connDict['sde_conn_ras1_geo'] = self.sde_conn_ras1_geo
        self.connDict['sde_conn_team_oereb'] = self.sde_conn_team_oereb
        self.connDict['sde_conn_vek1_oereb'] = self.sde_conn_vek1_oereb
        self.connDict['sde_conn_vek2_oereb'] = self.sde_conn_vek2_oereb        
        self.connDict['sde_conn_team_oereb2'] = self.sde_conn_team_oereb2
        self.connDict['sde_conn_vek1_oereb2'] = self.sde_conn_vek1_oereb2
        self.connDict['sde_conn_vek2_oereb2'] = self.sde_conn_vek2_oereb2       
        
        self.instanceDict = {}
        self.instanceDict['team'] = self.general_config['instances']['team']
        self.instanceDict['vek1'] = self.general_config['instances']['vek1']
        self.instanceDict['vek2'] = self.general_config['instances']['vek2']
        self.instanceDict['vek3'] = self.general_config['instances']['vek3']
        self.instanceDict['ras1'] = self.general_config['instances']['ras1']
        self.instanceDict['ras2'] = self.general_config['instances']['ras2']
        self.instanceDict['work'] = self.general_config['instances']['work']
        self.instanceDict['workh'] = self.general_config['instances']['workh']
        self.schemaDict = {}
        self.schema_geodb = self.general_config['users']['geodb']['schema']
        self.schema_geodb_dd = self.general_config['users']['geodb_dd']['schema']
        self.schema_norm = self.general_config['users']['norm']['schema']
        self.schema_oereb = self.general_config['users']['oereb']['schema']
        self.schema_oereb2 = self.general_config['users']['oereb2']['schema']
        self.schema_gdbp = self.general_config['users']['gdbp']['schema']
        self.schema_sysoem = self.general_config['users']['sysoem']['schema']
        self.schemaDict['geodb'] = self.schema_geodb
        self.schemaDict['geodb_dd'] = self.schema_geodb_dd
        self.schemaDict['norm'] = self.schema_norm
        self.schemaDict['oereb'] = self.schema_oereb
        self.schemaDict['oereb2'] = self.schema_oereb2
        self.schemaDict['gdbp'] = self.schema_gdbp
        self.schemaDict['sysoem'] = self.schema_sysoem
        self.userpwDict = {}
        self.userpwDict['norm'] = self.general_config['users']['norm']['password']
        self.userpwDict['oereb'] = self.general_config['users']['oereb']['password']
        self.userpwDict['oereb2'] = self.general_config['users']['oereb2']['password']
        self.userpwDict['geodb'] = self.general_config['users']['geodb']['password']
        self.userpwDict['geodb_dd'] = self.general_config['users']['geodb_dd']['password']
        self.userpwDict['gdbp'] = self.general_config['users']['gdbp']['password']
        self.userpwDict['sysoem'] = self.general_config['users']['sysoem']['password']
        
    def __get_oereb_infos(self):
        self.oereb_dict = {}
        self.logger.info("ÖREBK-Infos werden geholt.")
        oereb_tables_sql = "select ebecode, filter_field from gpr where GPRCODE='OEREB'"
        oereb_tables = []
        username = self.general_config['users']['oereb2']['username']
        pw = self.general_config['users']['oereb2']['password']
        db = self.general_config['instances']['workh']
        ora_conn = ora.connect(username, pw, db)
        ora_cursor = ora_conn.cursor()
        # Tabellennamen und Liefereinheiten-Feld holen
        ora_cursor.execute(oereb_tables_sql)
        tables = ora_cursor.fetchall()
        for table in tables:
            tbl_dict = {}
            tbl_dict['tablename'] = table[0]
            tbl_dict['filter_field'] = table[1]
            oereb_tables.append(tbl_dict)
        
        # ÖREB-Tickets des zu importierenden Geoprodukts holen
        # Wenn es keine zugehörigen Tickets hat, wird ein 
        # leerer String übergeben
        # Wenn es ein oder mehrere Tickets hat, werden sie als
        # kommagetrennter-String übergeben. 
        oereb_liefereinheiten_sql = "select ticket.liefereinheit from ticket left join liefereinheit on ticket.liefereinheit=liefereinheit.id left join workflow_gpr on liefereinheit.workflow=workflow_gpr.workflow where status=4 and workflow_gpr.gprcode='" + self.gpr + "'"
        ora_cursor.execute(oereb_liefereinheiten_sql)
        liefereinheiten = ora_cursor.fetchall()
        liefereinheiten_string = ""
        liefereinheiten_list = []
        for liefereinheit in liefereinheiten:
            liefereinheiten_list.append(unicode(liefereinheit[0]))
        if len(liefereinheiten_list) > 0:
            # Doppelte Liefereinheiten entfernen
            liefereinheiten_list =  list(set(liefereinheiten_list))
            liefereinheiten_string = "(" + ",".join(liefereinheiten_list) + ")"
        ora_cursor.close()
        ora_conn.close()
        self.oereb_dict['tabellen'] = oereb_tables
        self.oereb_dict['liefereinheiten'] = liefereinheiten_string
                
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        #Diverse Einträge im task_config generieren
        if not self.task_config.has_key("ausgefuehrte_funktionen"):
            self.task_config['ausgefuehrte_funktionen'] = []

        self.ebeVecList = []
        self.ebeRasList = []
        self.legList = []
        self.mxdList = []
        self.styleList = []
        self.fontList = []
        self.zusatzList = []
        self.__define_connections()               
        self.__get_importe_dd()
        self.__get_gpr_info()
        self.__get_ebe_dd()
        self.__get_wtb_dd()
        self.__define_quelle_ziel_begleitdaten()
        self.__get_mxd_dd("DE")
        self.__get_mxd_dd("FR")
        self.__get_leg_dd()        
        self.__get_fak_begleitdaten()
        self.__define_qs()
        self.__get_oereb_infos()
        
        self.task_config['connections'] = self.connDict
        self.task_config['instances'] = self.instanceDict
        self.task_config['schema'] = self.schemaDict
        self.task_config['users'] = self.userpwDict
        self.task_config['gpr'] = self.gpr
        self.task_config['gzs_objectid'] = self.gzs_objectid
        self.task_config['zeitstand'] = self.zeitstand
        self.task_config['zeitstand_jahr'] = self.jahr
        self.task_config['zeitstand_version'] = self.version
        self.task_config['rolle'] = self.rolle_freigabe
        self.task_config['vektor_ebenen'] = self.ebeVecList
        self.task_config['raster_ebenen'] = self.ebeRasList
        self.task_config['legende'] = self.legList
        self.task_config['mxd'] = self.mxdList
        self.task_config['ziel'] = {'ziel_begleitdaten_gpr': self.ziel_begleitdaten_gpr, 'ziel_begleitdaten_mxd': self.ziel_begleitdaten_mxd, 'ziel_begleitdaten_symbol': self.ziel_begleitdaten_symbol, 'ziel_begleitdaten_zusatzdaten': self.ziel_begleitdaten_zusatzdaten}
        self.task_config['style'] = self.styleList
        self.task_config['font'] = self.fontList
        self.task_config['zusatzdaten'] = self.zusatzList
        self.task_config['ziel'] = self.zielDict
        self.task_config['qs'] = self.qsDict
        self.task_config['default_tolerance'] = self.default_tolerance
        self.task_config['default_resolution'] = self.default_resolution
        self.task_config['spatial_reference'] = self.spatial_reference
        self.task_config['oereb'] = self.oereb_dict
        self.finish()  
       
    def __load_task_config(self):
        '''
        Lädt die Task-Config aus der JSON-Datei.
        '''
        f = open(self.task_config['task_config_file'], "r")
        js = json.load(f)
        f.close
                
        if len(js) > 0:
                # die Variable js darf nicht einfach self.task_config
                # zugewiesen werden, da damit ein neues Objekt erzeugt
                # wird. self.task_config  ist dann in den Usecases nicht
                # mehr identisch. Damit kein neues Objekt erzeugt wird,
                # wird das bestehende geleert (clear) und dann mit den
                # Inhalten aus der Variable js gefüllt.
                self.task_config.clear()
                self.task_config.update(js)
                # Alle Passwörter im JSON-File sind verschlüsselt.
                # Sie müssen deshalb entschlüsselt werden.
                crypter = Crypter()
                for key, value in self.task_config['users'].iteritems():
                    self.task_config['users'][key] = crypter.decrypt(value)
                
