# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import os
import json
import codecs
import cx_Oracle as ora
from iLader.helpers import OracleHelper
from iLader.helpers import PostgresHelper

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
        TemplateFunction.__init__(self, task_config, general_config)

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
        self.result = OracleHelper.readOracleSQL(self.db, self.username, self.password, self.sql_name)  
    
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
        self.quelle_begleitdatenraster = os.path.join(self.general_config['quelle_begleitdaten'], self.gpr, 'work', 'symbol','Rasterdataset')
       
    
    def __get_ebe_dd(self):
        self.sql_dd_ebe = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, g.dat_bezeichnung_de, d.EZS_OBJECTID from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"   
        self.__db_connect('team', 'geodb_dd', self.sql_dd_ebe)
        for row in self.result:
            self.logger.info(row)
            ebeVecDict = {}
            ebeRasDict = {}
            ebeCacheDict = {}
            gpr = row[0].decode('cp1252')
            ebe = row[1].decode('cp1252')
            ezs_objectid = unicode(row[5])
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
            if datentyp != 'Rastermosaik' and datentyp != 'Rasterkatalog' and datentyp != 'Mosaicdataset' and datentyp != 'Cache':
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
                
                # Wertetabellen-Infos auslesen
                # Muss pro Ebene geschehen, da die View-Erstellung den Bezug zur Ebene braucht.
                wertetabellenList = []
                sql_wertetabellen = "select w.WTB_BEZEICHNUNG, w.WTB_JOIN_FOREIGNKEY, w.WTB_JOIN_PRIMARYKEY, w.wtb_join_typ from TB_WERTETABELLE w where w.EZS_OBJECTID=" + ezs_objectid
                wertetabellen_results = OracleHelper.readOracleSQL(self.general_config['instances']['team'], self.general_config['users']['geodb_dd']['username'], self.general_config['users']['geodb_dd']['password'], sql_wertetabellen)
                wertetabellenDict = {}
                for wt in wertetabellen_results:
                    wertetabellenDict = {
                        "wtb_code": wt[0],
                        "wtb_foreignkey": wt[1],
                        "wtb_primarykey": wt[2],
                        "wtb_jointype": wt[3]
                    }
                    wertetabellenList.append(wertetabellenDict)
                
                ebeVecDict['wertetabellen'] = wertetabellenList

                self.ebeVecList.append(ebeVecDict)            
            elif datentyp == 'Rastermosaik': #TODO: ev. später Rasterdataset
                ebeRasDict['datentyp'] = datentyp
                ebeRasDict['gpr_ebe'] = gpr_ebe
                ebeRasDict['quelle'] = quelle
                ebeRasDict['ziel_ras1']= ziel_ras1_akt
                ebeRasDict['ziel_ras1_zs']= ziel_ras1_zs
                self.ebeRasList.append(ebeRasDict)
            # Cache-Ebenen kommen nicht in die Liste der Vektor-Ebenen
            # Damit werden diese Ebenen automatisch nirgends kopiert
            elif datentyp == "Cache":
                ebeCacheDict['gpr_ebe'] = gpr_ebe
                ebeCacheDict['datentyp'] = datentyp
                self.ebeCacheList.append(ebeCacheDict)
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
        # Es wird nur im SYMBOL-Verzeichnis gesucht. Unterverzeichnisse werden ignoriert.
        symbol_dir_files = [f for f in os.listdir(self.quelle_begleitdaten_symbol) if os.path.isfile(os.path.join(self.quelle_begleitdaten_symbol, f))]
        for symbol_dir_file in symbol_dir_files:
            if symbol_dir_file.lower().endswith('.style'):
                self.logger.info(symbol_dir_file)
                styleDict = {}
                styleDict['name'] = symbol_dir_file
                styleDict['quelle'] = os.path.join(self.quelle_begleitdaten_symbol, symbol_dir_file)
                self.style_ziel_akt = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + symbol_dir_file)
                styleDict['ziel_akt'] = self.style_ziel_akt.upper()
                self.style_zs = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + self.zeitstand + "_" + symbol_dir_file)
                styleDict['ziel_zs'] = self.style_zs.upper()
                self.styleList.append(styleDict)
            elif symbol_dir_file.lower().endswith('.ttf'):
                self.logger.info(symbol_dir_file)
                fontDict = {}
                fontDict['name'] = symbol_dir_file
                fontDict['quelle'] = os.path.join(self.quelle_begleitdaten_symbol, symbol_dir_file)
                self.font_akt = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + symbol_dir_file)
                fontDict['ziel_akt'] = self.font_akt.upper()
                self.font_zs = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + self.zeitstand + "_" + symbol_dir_file)
                fontDict['ziel_zs'] = self.font_zs.upper()
                self.fontList.append(fontDict)      
    
    def __get_fak_zusatzdaten(self):
        self.logger.info("Prüfe ob Zusatzdaten vorhanden auf:")
        self.zusatzDict = {}
        if os.path.exists(self.quelle_begleitdaten_zusatzdaten):
            self.logger.info("Zusatzdaten vorhanden")
            self.zusatzDict['quelle'] = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_zusatzdaten'])
            self.zusatzDict['ziel'] = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_zusatzdaten'], self.zeitstand)
            
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
            wtbDict['datentyp']= "Wertetabelle"
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
        self.instanceDict['oereb'] = self.general_config['instances']['oereb']
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
        self.task_config['db_vek1_pg'] = self.general_config['db_vek1_pg']
        self.task_config['db_vek2_pg'] = self.general_config['db_vek2_pg']
        self.task_config['db_team_pg'] = self.general_config['db_team_pg']
        self.task_config['port_pg'] = self.general_config['port_pg']

    def __get_oereb_tables(self, oereb_tables_sql):
        oereb_tables = []
        tables = PostgresHelper.db_sql(self=self, host=self.general_config['instances']['oereb'], db=self.general_config['db_work_pg'], port=self.general_config['port_pg'], db_user=self.general_config['users']['oereb']['username'], pw=self.general_config['users']['oereb']['password'], sql_query=oereb_tables_sql, fetch=True, fetchall=True)
        for table in tables:
            tbl_dict = {}
            tbl_dict['tablename'] = table[0]
            tbl_dict['filter_field'] =  table[1]
            oereb_tables.append(tbl_dict)
        
        return oereb_tables

    def __get_oereb_liefereinheiten(self, oereb_liefereinheiten_sql):
        oereb_liefereinheiten = []
        liefereinheiten = PostgresHelper.db_sql(self=self, host=self.general_config['instances']['oereb'], db=self.general_config['db_work_pg'], port=self.general_config['port_pg'], db_user=self.general_config['users']['oereb']['username'], pw=self.general_config['users']['oereb']['password'], sql_query=oereb_liefereinheiten_sql, fetch=True, fetchall=True)
        for liefereinheit in liefereinheiten:
            oereb_liefereinheiten.append(unicode(liefereinheit[0]))
        
        return oereb_liefereinheiten

    def __get_oereb_schemas(self, oereb_schemas_sql):
        oereb_schemas = []
        schemas = PostgresHelper.db_sql(self=self, host=self.general_config['instances']['oereb'], db=self.general_config['db_work_pg'], port=self.general_config['port_pg'], db_user=self.general_config['users']['oereb']['username'], pw=self.general_config['users']['oereb']['password'], sql_query=oereb_schemas_sql, fetch=True, fetchall=True)
        for schema in schemas:
            oereb_schemas.append(schema[0])
        
        return oereb_schemas

    def __get_oereb_infos(self):
        self.oereb_dict = {}
        self.logger.info("ÖREBK-Infos werden geholt.")
        # Tabellen der Oracle-Transferstruktur werden geholt
        oereb_tables_ora_sql = "select ebecode, filter_field from oereb.gpr where gprcode='OEREB' ORDER BY EBEORDER ASC"
        oereb_tables_ora = self.__get_oereb_tables(oereb_tables_ora_sql)
        # Tabellen der PostGIS-Transferstruktur werden geholt
        oereb_tables_ora_sql = "select ebecode, filter_field from oereb.gpr where gprcode='OEREB_PG' ORDER BY EBEORDER ASC"
        oereb_tables_pg = self.__get_oereb_tables(oereb_tables_ora_sql)
        # Liefereinheiten werden geholt und als String formatiert, der
        # in einer WHERE-Clause (IN) verwendet werden kann.
        oereb_liefereinheiten_sql = "select distinct ticket.liefereinheit from oereb.ticket left join oereb.liefereinheit on ticket.liefereinheit=liefereinheit.id left join oereb.workflow_gpr on liefereinheit.workflow=workflow_gpr.workflow where status=4 and oereb.workflow_gpr.gprcode='%s'" % (self.gpr)
        liefereinheiten = self.__get_oereb_liefereinheiten(oereb_liefereinheiten_sql)
        # Schemas werden geholt
        oereb_schemas_sql = "select distinct workflow_schema.schema from oereb.ticket left join oereb.liefereinheit on ticket.liefereinheit=liefereinheit.id left join oereb.workflow_gpr on liefereinheit.workflow=workflow_gpr.workflow left join oereb.workflow_schema on liefereinheit.workflow=workflow_schema.workflow where status=4 and workflow_gpr.gprcode='%s'" % (self.gpr)
        schemas = self.__get_oereb_schemas(oereb_schemas_sql)
        # Config-Dictionary wird gefüllt.
        self.oereb_dict['tabellen_ora'] = oereb_tables_ora
        self.oereb_dict['tabellen_pg'] = oereb_tables_pg
        self.oereb_dict['liefereinheiten'] = "(" + ",".join(liefereinheiten) + ")"
        self.oereb_dict['schemas'] = schemas
                
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        #Diverse Einträge im task_config generieren
        if not self.task_config.has_key("ausgefuehrte_funktionen"):
            self.task_config['ausgefuehrte_funktionen'] = []

        self.ebeVecList = []
        self.ebeRasList = []
        self.ebeCacheList = []
        self.legList = []
        self.mxdList = []
        self.styleList = []
        self.fontList = []
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
        self.__get_fak_zusatzdaten()
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
        self.task_config['cache_ebenen'] = self.ebeCacheList
        self.task_config['legende'] = self.legList
        self.task_config['mxd'] = self.mxdList
        self.task_config['ziel'] = {'ziel_begleitdaten_gpr': self.ziel_begleitdaten_gpr, 'ziel_begleitdaten_mxd': self.ziel_begleitdaten_mxd, 'ziel_begleitdaten_symbol': self.ziel_begleitdaten_symbol, 'ziel_begleitdaten_zusatzdaten': self.ziel_begleitdaten_zusatzdaten}
        self.task_config['style'] = self.styleList
        self.task_config['font'] = self.fontList
        self.task_config['zusatzdaten'] = self.zusatzDict
        self.task_config['ziel'] = self.zielDict
        self.task_config['quelle_begleitdatenraster'] = self.quelle_begleitdatenraster
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
        with codecs.open(self.task_config['task_config_file'], "r", "utf-8") as json_file:
            json_content = json.load(json_file)
                
        if len(json_content) > 0:
                # die Variable js darf nicht einfach self.task_config
                # zugewiesen werden, da damit ein neues Objekt erzeugt
                # wird. self.task_config  ist dann in den Usecases nicht
                # mehr identisch. Damit kein neues Objekt erzeugt wird,
                # wird das bestehende geleert (clear) und dann mit den
                # Inhalten aus der Variable js gefüllt.
                self.task_config.clear()
                self.task_config.update(json_content)                
