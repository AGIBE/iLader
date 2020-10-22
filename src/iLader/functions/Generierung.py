# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import os
import json
import codecs
import sys

class Generierung(TemplateFunction):
    '''
    Sammelt sämtliche benötigten Informationen zusammen aus:
    - DataDictionary
    - General Config
    - GeoDBProzess
    - ÖREB-Kataster
    Die Informationen werden in die task_config geschrieben.
    '''
    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        :param general_config: Allgemeine Config (v.a. DB-Connections)
        '''
        self.name = "Generierung"
        TemplateFunction.__init__(self, task_config, general_config)

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
    
    def __get_gzsobjectid_from_task(self):
        self.logger.info("Hole GZS_OBJECTID aus TB_TASK")
        gzs_objectid_sql = "select gzs_objectid from geodb_dd.tb_task where task_objectid=%s" % (unicode(self.task_config['task_id']))
        gzs_objectid_results = self.general_config.connections['TEAM_GEODB_DD_ORA'].db_read(gzs_objectid_sql)
        if len(gzs_objectid_results) == 1:
            return gzs_objectid_results[0][0]
        else:
            self.logger.error("In TB_TASK wurde kein GZS_OBJECTID gefunden!")
            sys.exit()
    
    def __get_gprinfo_from_dd(self):
        '''
        Diese Funktion sucht die Informationen auf Stufe Geoprodukt aus dem DD der GeoDB
        und aus GeoDBprozess zusammen
        DD GeoDB: Geoproduktcode, Jahr, Version
        GeoDBprozess: Rolle, sofern eine definiert ist, ansonsten Standardrolle
        Ausserdem werden ein paar Parameter aus der Config in die Task-Config übernommen
        '''
        self.logger.info("Hole Infos aus DD (Geoprodukt-Code, Zeitstand)")
        geoprodukt_dd_sql = "SELECT a.gpr_bezeichnung, b.gzs_jahr, b.gzs_version, a.gpr_viewer_freigabe from geodb_dd.tb_geoprodukt_zeitstand b join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid where b.gzs_objectid = %s" % (self.gzs_objectid)
        geoprodukt_dd_results = self.general_config.connections['TEAM_GEODB_DD_ORA'].db_read(geoprodukt_dd_sql)
        if len(geoprodukt_dd_results) == 1:
            gpr = geoprodukt_dd_results[0]
            jahr = unicode(geoprodukt_dd_results[1])
            version = unicode(geoprodukt_dd_results[2]).zfill(2)
            zeitstand = "%s_%s" % (jahr, version)
        else:
            self.logger.error("Infos in TB_GEOPRODUKT konnten nicht gefunden werden.")
            self.logger.error("Anzahl zurückgegebene Records: %s" % (unicode(len(geoprodukt_dd_results))))
            sys.exit()
        
        self.logger.info("Lese Rolle aus GeoDBProzess aus.")
        gdpb_rolle_sql = "SELECT a.db_rollen from gdbp.geoprodukte a where a.code = '%s'" % (gpr)
        gdbp_rolle_results = self.general_config.connections['WORK_GDBP_ORA'].db_read(gdpb_rolle_sql)
        if len(gdbp_rolle_results) == 1:
            if gdbp_rolle_results[0][0]:
                rolle_freigabe = gdbp_rolle_results[0][0]
            else:
                rolle_freigabe = self.general_config['standard_rolle']
        else:
            self.logger.info("Infos in GDBP konnten nicht gefunden werden.")
            self.logger.info("Anzahl zurückgegebene Records: %s" % (unicode(len(gdbp_rolle_results))))
            sys.exit()

        return (gpr, jahr, version, zeitstand, rolle_freigabe)
    
    def __get_ebeinfo_from_dd(self):
        '''
        Holt die Infos zu den Ebenen aus dem DD (Bezeichnungen, Datentyp, Wertetabellen etc.)
        '''
        self.logger("Hole Ebenen-Infos aus dem DD.")
        ebene_dd_sql = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, g.dat_bezeichnung_de, d.EZS_OBJECTID from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid where b.gzs_objectid = %s" % (self.gzs_objectid)
        ebene_dd_results = self.general_config.connections['TEAM_GEODB_DD_ORA'].db_read(ebene_dd_sql)
        ebeVecList, ebeRasList, ebeCacheList = [], [], []
        if len(ebene_dd_results) == 0:
            self.logger.info("Es wurden im DD keine Ebenen-Informationen gefunden.")
            sys.exit()
        else:
            for ebene_dd_result in ebene_dd_results:
                ebe = ebene_dd_result[1]
                self.logger("Hole Infos für Ebene %s" % (ebe))
                ezs_objectid = unicode(ebene_dd_result[5])
                datentyp = ebene_dd_result[4]
                gpr_ebe = unicode(self.gpr) + "_" + unicode(ebe)
                quelle_schema_gpr_ebe = self.schemaDict['norm'] + "." + gpr_ebe
                quelle = os.path.join(self.connDict['sde_conn_norm'], quelle_schema_gpr_ebe)
                ziel_schema_gpr_ebe = self.schemaDict['geodb'] + "." + gpr_ebe
                ziel_schema_gpr_ebe_zs = ziel_schema_gpr_ebe + "_" + self.zeitstand     
                if datentyp not in ('Rastermosaik', 'Rasterkatalog', 'Mosaicdataset', 'Cache'):
                    self.logger.info("Ebenen ist eine Vektor-Ebene.")
                    self.logger.info("Deshalb werden nun die Index-Informationen geholt.")
                    ebene_index_gdbp_sql = 'SELECT b.felder, DECODE(b."unique", 1, \'True\', 2, \'False\') "unique" from gdbp.index_attribut b join gdbp.geoprodukte a on b.id_geoprodukt = a.id_geoprodukt where a.code = \'%s\' and b.ebene = \'%s\'' % (self.gpr, ebe)
                    ebene_index_gdbp_results = self.general_config.connections['WORK_GDBP_ORA'].db_read(ebene_index_gdbp_sql)
                    indList = []
                    for ebene_index_gdbp_result in ebene_index_gdbp_results:
                        indDict = {
                            'attribute': ebene_index_gdbp_result[0],
                            'unique': ebene_index_gdbp_result[1]
                        }
                        indList.append(indDict)
                    ebeVecDict = {
                        'indices': indList,
                        'datentyp': datentyp,
                        'gpr_ebe': gpr_ebe,
                        'quelle': quelle,
                        'ziel_vek1': os.path.join(self.connDict['sde_conn_vek1'], ziel_schema_gpr_ebe),
                        'ziel_vek2': os.path.join(self.connDict['sde_conn_vek2'], ziel_schema_gpr_ebe),
                        'ziel_vek3': os.path.join(self.connDict['sde_conn_vek3'], ziel_schema_gpr_ebe_zs)
                    }
                    
                    # Wertetabellen-Infos auslesen
                    # Muss pro Ebene geschehen, da die View-Erstellung den Bezug zur Ebene braucht.
                    self.logger.info("Infos zu den Wertetabellen werden geholt.")
                    wertetabellenList = []
                    ebene_wertetabellen_sql = "select w.WTB_BEZEICHNUNG, w.WTB_JOIN_FOREIGNKEY, w.WTB_JOIN_PRIMARYKEY, w.wtb_join_typ from TB_WERTETABELLE w where w.EZS_OBJECTID=%s" % (ezs_objectid)
                    ebene_wertetabellen_results = self.general_config.connections['TEAM_GEODB_DD_ORA'].db_read(ebene_wertetabellen_sql)
                    for ebene_wertetabelle in ebene_wertetabellen_results:
                        wertetabellenList.append({
                            "wtb_code": ebene_wertetabelle[0],
                            "wtb_foreignkey": ebene_wertetabelle[1],
                            "wtb_primarykey": ebene_wertetabelle[2],
                            "wtb_jointype": ebene_wertetabelle[3]
                        })
                    ebeVecDict['wertetabellen'] = wertetabellenList
                    ebeVecList.append(ebeVecDict)            

                elif datentyp == 'Rastermosaik': #TODO: ev. später Rasterdataset
                    self.logger.info("Ebene ist eine Rasterebene.")
                    ebeRasDict = {
                        'datentyp': datentyp,
                        'gpr_ebe': gpr_ebe,
                        'quelle': quelle,
                        'ziel_ras1': os.path.join(self.connDict['sde_conn_ras1'], ziel_schema_gpr_ebe),
                        'ziel_ras1_zs': os.path.join(self.connDict['sde_conn_ras1'], ziel_schema_gpr_ebe_zs)
                    }
                    ebeRasList.append(ebeRasDict)

                # Cache-Ebenen kommen nicht in die Liste der Vektor-Ebenen
                # Damit werden diese Ebenen automatisch nirgends kopiert
                elif datentyp == "Cache":
                    self.logger.info("Ebene ist eine Cache-Ebene")
                    ebeCacheDict = {
                        'gpr_ebe': gpr_ebe,
                        'datentyp': datentyp
                    }
                    ebeCacheList.append(ebeCacheDict)
        return (ebeVecList, ebeRasList, ebeCacheList)
                    
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
        self.logger("Legendeninfos werden aus dem DD geholt.")
        legenden_dd_sql = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, f.leg_bezeichnung, h.spr_kuerzel, g.dat_objectid from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid JOIN geodb_dd.tb_legende f on f.ezs_objectid = d.ezs_objectid JOIN geodb_dd.tb_sprache h on h.spr_objectid = f.spr_objectid where b.gzs_objectid = %s" % (self.gzs_objectid)
        legenden_dd_results = self.general_config.connections['TEAM_GEODB_DD_ORA'].db_read(legenden_dd_sql)
        legends = []
        for legende in legenden_dd_results:
            ebe_code = legende[1]
            leg_code = legende[4]
            leg_lang = legende[5]
            leg_datentyp = legende[6]

            # Mosaic Datasets müssen anders behandelt werden
            if leg_datentyp != 9:
                symbol_name = "%s_%s_%s_%s.lyr" % (self.gpr, ebe_code, leg_code, leg_lang)
                symbol_name_akt = "AKTUELL_%s_%s_%s_%s.lyr" % (self.gpr, ebe_code, leg_code, leg_lang)
                symbol_name_zs = "%s_%s_%s_%s_%s.lyr" % (self.gpr, ebe_code, self.zeitstand, leg_code, leg_lang)
                quelle_symbol =  os.path.join(self.quelle_begleitdaten_symbol, symbol_name)
                ziel_symbol_akt = os.path.join(self.ziel_begleitdaten_symbol, symbol_name_akt)
                ziel_symbol_zs = os.path.join(self.ziel_begleitdaten_symbol, symbol_name_zs)
            else:
                symbol_name = "%s_%s_%s_%s_%s.lyr" % (self.gpr, ebe_code, self.zeitstand, leg_code, leg_lang)
                symbol_name_zs = symbol_name
                symbol_name_akt = "DELETE_%s_%s_%s_%s.lyr" % (self.gpr, ebe_code, leg_code, leg_lang)
                quelle_symbol =  os.path.join(self.quelle_begleitdaten_symbol, symbol_name)
                ziel_symbol_akt = os.path.join(self.ziel_begleitdaten_symbol, symbol_name_akt)
                ziel_symbol_zs = os.path.join(self.ziel_begleitdaten_symbol, symbol_name_zs)

            legDict = {
                'name': symbol_name.lower(),
                'quelle': quelle_symbol.lower(),
                'ziel_akt': ziel_symbol_akt.upper(),
                'ziel_zs': ziel_symbol_zs.upper()
            }
            legends.append(legDict)

        return legends
    
    def __get_mxd_dd(self, lang):
        '''
        Diese Funktion bildet die notwendigen MXD-Namen und Pfade in einer Sprache.
        Die Sprache muss übergeben werden.
        '''
        mxd_lang = "%s_%s.mxd" % (self.gpr, lang)
        quelle_mxd_lang = os.path.join(self.quelle_begleitdaten_mxd, mxd_lang)
        mxd_lang_akt = "AKTUELL_%s_%s_%s.mxd" % (self.gpr, self.gpr, lang)
        ziel_mxd_lang_akt = os.path.join(self.ziel_begleitdaten_mxd, mxd_lang_akt)
        mxd_lang_zs = "%s_%s_%s_%s.mxd" % (self.gpr, self.zeitstand, self.gpr, lang)
        ziel_mxd_lang_zs = os.path.join(self.ziel_begleitdaten_mxd, mxd_lang_zs)
        mxdDict = {
            'name': mxd_lang,
            'quelle': quelle_mxd_lang,
            'ziel_akt': ziel_mxd_lang_akt.upper(),
            'ziel_zs': ziel_mxd_lang_zs.upper()             
        }
        return mxdDict
    
    def __get_fak_begleitdaten(self):
        """
        Diese Funktion sucht alle übrigen Begleit-dDaten im Symbol-Verzeichnis zusammen.
        Dies können sein: Style-Files, Fonts
        Lyr-Files werden ausgelassen. Sie werden an anderer Stelle bearbeitet.
        Es wird nur im SYMBOL-Verzeichnis gesucht. Unterverzeichnisse werden ignoriert.
        """
        self.logger.info("Suche übrige Begleitdaten (Styles, Fonts)")
        symbol_dir_files = [f for f in os.listdir(self.quelle_begleitdaten_symbol) if os.path.isfile(os.path.join(self.quelle_begleitdaten_symbol, f))]
        stylesList, fontsList = [], []
        for symbol_dir_file in symbol_dir_files:
            self.logger.info(symbol_dir_file)
            style_ziel_akt = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + symbol_dir_file)
            style_zs = os.path.join(self.ziel_begleitdaten_symbol, self.gpr + "_" + self.zeitstand + "_" + symbol_dir_file)
            fileDict = {
                'name': symbol_dir_file,
                'quelle': os.path.join(self.quelle_begleitdaten_symbol, symbol_dir_file),
                'ziel_akt': style_ziel_akt.upper(),
                'ziel_zs': style_zs.upper()
            }
            if symbol_dir_file.lower().endswith('.style'):
                stylesList.append(fileDict)
            elif symbol_dir_file.lower().endswith('.ttf'):
                fontsList.append(fileDict)
            
        return stylesList, fontsList
    
    def __get_fak_zusatzdaten(self):
        '''
        Diese Funktion prüft, ob das Zusatzdaten-Verzeichnis vorhanden ist.
        Ist das der Fall, wird es in die Task-Config aufgenommen, damit es
        dann kopiert wird.
        '''
        self.logger.info("Prüfe ob Zusatzdaten vorhanden auf:")
        zusatzDict = {}
        if os.path.exists(self.quelle_begleitdaten_zusatzdaten):
            self.logger.info("Zusatzdaten vorhanden")
            zusatzDict['quelle'] = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_zusatzdaten'])
            zusatzDict['ziel'] = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_zusatzdaten'], self.zeitstand)
        return zusatzDict
            
    def __define_quelle_ziel_begleitdaten(self):
        """
        Diese Funktion definiert verschiedene Pfade in Bezug auf die Begleitdaten
        """
        zielDict = {}
        self.quelle_begleitdaten_gpr = os.path.join(self.general_config['quelle_begleitdaten'], self.gpr, self.general_config['quelle_begleitdaten_work'])
        self.quelle_begleitdaten_mxd = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_mxd'])
        self.quelle_begleitdaten_symbol = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_symbol'])
        self.quelle_begleitdaten_zusatzdaten = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_zusatzdaten'])
        self.ziel_begleitdaten_gpr = os.path.join(self.general_config['ziel_begleitdaten'], self.gpr)
        self.ziel_begleitdaten_mxd = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_mxd'])
        self.ziel_begleitdaten_symbol = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_symbol'])
        self.ziel_begleitdaten_zusatzdaten = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_zusatzdaten'])
        zielDict = {
            'ziel_begleitdaten_gpr': self.ziel_begleitdaten_gpr,
            'ziel_begleitdaten_mxd': self.ziel_begleitdaten_mxd,
            'ziel_begleitdaten_symbol': self.ziel_begleitdaten_symbol,
            'ziel_begleitdaten_zusatzdaten': self.ziel_begleitdaten_zusatzdaten
        }
        return zielDict    
         
    def __get_wtb_dd(self):
        """
        Diese Funktion ermittelt alle Wertetabellen und schreibt diese so in
        die Task-Config, damit sie danach wie andere Vektor-Ebenen kopiert werden.
        Jede Wertetabellen wird genau einmal übernommen, auch wenn sie mehrmals
        im DD als Wertetabellen genutzt wird. Das reduziert die Importzeiten.
        """
        self.logger.info("Wertetabellen-Infos werden geholt.")
        wtbList = []
        wertetabellen_dd_sql = "SELECT DISTINCT e.wtb_bezeichnung from geodb_dd.tb_wertetabelle e join geodb_dd.tb_ebene_zeitstand d on e.ezs_objectid = d.ezs_objectid join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid where b.gzs_objectid = %s ORDER BY e.WTB_BEZEICHNUNG" % (self.gzs_objectid)
        wertetabellen_dd_results = self.general_config.connections['TEAM_GEODB_DD_ORA'].db_read(wertetabellen_dd_sql)
        for wertetabelle in wertetabellen_dd_results:
            wtb_code = wertetabelle[0]
            self.logger.info("Wertetabelle %s" % (wtb_code))
            gpr_wtb =  "%s_%s" % (self.gpr, wtb_code)
            quelle = os.path.join(self.connDict['sde_conn_norm'], self.schemaDict['norm'] + "." + gpr_wtb)
            ziel_schema_gpr_wtb = self.schemaDict['geodb'] + "." + gpr_wtb
            ziel_vek1 = os.path.join(self.connDict['sde_conn_vek1'], ziel_schema_gpr_wtb)
            ziel_vek2 = os.path.join(self.connDict['sde_conn_vek2'], ziel_schema_gpr_wtb)
            ziel_vek3 = os.path.join(self.connDict['sde_conn_vek3'], ziel_schema_gpr_wtb + "_" + self.zeitstand)
            
            # Wertetabellen können u.U. auch Indizes haben
            wertetabelle_index_gdbp_sql = 'SELECT b.felder, DECODE(b."unique", 1, \'True\', 2, \'False\') "unique" from gdbp.index_attribut b join gdbp.geoprodukte a on b.id_geoprodukt = a.id_geoprodukt where a.code = \'%s\' and b.ebene = \'%s\'' % (self.gpr, wtb_code)
            wertetabelle_index_gdbp_results = self.general_config.connections['WORK_GDBP_ORA'].db_read(wertetabelle_index_gdbp_sql)
            indList = []
            for wertetabelle_index_gdbp_result in wertetabelle_index_gdbp_results:
                indDict = {
                    'attribute': wertetabelle_index_gdbp_result[0],
                    'unique': wertetabelle_index_gdbp_result[1]
                }
                indList.append(indDict)
            wtbDict = {
                'indices': indList,
                'datentyp': "Wertetabelle",
                'gpr_ebe': gpr_wtb,
                'quelle': quelle,
                'ziel_vek1': ziel_vek1,
                'ziel_vek2': ziel_vek2,
                'ziel_vek3': ziel_vek3
            }
            wtbList.append(wtbDict)
        
        return wtbList
               
    def __define_connections(self):
        sde_connection_directory = os.path.join(os.environ['GEODBIMPORTSECRET'], 'connections')
        connDict = {
            'sde_conn_team_dd': os.path.join(sde_connection_directory, 'team_dd.sde'),
            'sde_conn_vek1': os.path.join(sde_connection_directory, 'vek1.sde'),
            'sde_conn_vek2': os.path.join(sde_connection_directory, 'vek2.sde'),
            'sde_conn_vek3': os.path.join(sde_connection_directory, 'vek3.sde'),
            'sde_conn_ras1': os.path.join(sde_connection_directory, 'ras1.sde'),
            'sde_conn_ras2': os.path.join(sde_connection_directory, 'ras2.sde'),
            'sde_conn_norm': os.path.join(sde_connection_directory, 'norm.sde'),
            'sde_conn_vek1_geo': os.path.join(sde_connection_directory, 'vek1_geo.sde'),
            'sde_conn_vek2_geo': os.path.join(sde_connection_directory, 'vek2_geo.sde'),
            'sde_conn_vek3_geo': os.path.join(sde_connection_directory, 'vek3_geo.sde'),
            'sde_conn_ras1_geo': os.path.join(sde_connection_directory, 'ras1_geo.sde'),
            'sde_conn_team_oereb2': os.path.join(sde_connection_directory, 'team_oereb2.sde'),
            'sde_conn_vek1_oereb2': os.path.join(sde_connection_directory, 'vek1_oereb2.sde'),
            'sde_conn_vek2_oereb2': os.path.join(sde_connection_directory, 'vek2_oereb2.sde')
        }  
        
        instanceDict = {
            'team': self.general_config['connection_infos']['db']['team']['ora_db'],
            'vek1': self.general_config['connection_infos']['db']['vek1']['ora_db'],
            'vek2': self.general_config['connection_infos']['db']['vek2']['ora_db'],
            'vek3': self.general_config['connection_infos']['db']['vek3']['ora_db'],
            'ras1': self.general_config['connection_infos']['db']['ras1']['ora_db'],
            'ras2': self.general_config['connection_infos']['db']['ras2']['ora_db'],
            'work': self.general_config['connection_infos']['db']['work']['ora_db'],
            'oereb': self.general_config['connection_infos']['db']['team']['pg_host']
        }
        
        schemaDict = {
            'geodb': self.general_config['connection_infos']['user']['geodb']['username'],
            'geodb_dd': self.general_config['connection_infos']['user']['geodb_dd']['username'],
            'norm': self.general_config['connection_infos']['user']['norm']['username'],
            'oereb': self.general_config['connection_infos']['user']['oereb']['username'],
            'oereb2': self.general_config['connection_infos']['user']['oereb2']['username'],
            'gdbp': self.general_config['connection_infos']['user']['gdbp']['username'],
            'sysoem': self.general_config['connection_infos']['user']['sysoem']['username']
        }
        
        userpwDict = {
            'norm': self.general_config['connection_infos']['user']['norm']['password'],
            'oereb': self.general_config['connection_infos']['user']['oereb']['password'],
            'oereb2': self.general_config['connection_infos']['user']['oereb2']['password'],
            'geodb': self.general_config['connection_infos']['user']['geodb']['password'],
            'geodb_dd': self.general_config['connection_infos']['user']['geodb_dd']['password'],
            'gdbp': self.general_config['connection_infos']['user']['gdbp']['password'],
            'sysoem': self.general_config['connection_infos']['user']['sysoem']['password']
        }

        return (connDict, instanceDict, schemaDict, userpwDict)


    def __get_oereb_tables(self, oereb_tables_sql):
        oereb_tables = []
        oereb_tables_results = self.general_config['connections']['WORK_OEREB_PG'].db_read(oereb_tables_sql)
        for oereb_table in oereb_tables_results:
            tbl_dict = {
                'tablename': oereb_table[0],
                'filter_field':  oereb_table[1]
            }
            oereb_tables.append(tbl_dict)
        
        return oereb_tables

    def __get_oereb_liefereinheiten(self, oereb_liefereinheiten_sql):
        oereb_liefereinheiten_results = self.general_config['connections']['WORK_OEREB_PG'].db_read(oereb_liefereinheiten_sql)
        return [unicode(le[0]) for le in oereb_liefereinheiten_results]

    def __get_oereb_schemas(self, oereb_schemas_sql):
        oereb_schemas_results = self.general_config['connections']['WORK_OEREB_PG'].db_read(oereb_schemas_sql)
        return [schema[0] for schema in oereb_schemas_results]

    def __get_oereb_infos(self):
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
        oerebDict = {
            'tabellen_ora': oereb_tables_ora,
            'tabellen_pg': oereb_tables_pg,
            'liefereinheiten': "(" + ",".join(liefereinheiten) + ")",
            'schemas': schemas
        }

        return oerebDict
                
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        #Diverse Einträge im task_config generieren
        if not self.task_config.has_key("ausgefuehrte_funktionen"):
            self.task_config['ausgefuehrte_funktionen'] = []

        self.connDict, self.instanceDict, self.schemaDict, self.userpwDict = self.__define_connections()
        self.task_config['connections'] = self.connDict
        self.task_config['instances'] = self.instanceDict
        self.task_config['schema'] = self.schemaDict
        self.task_config['users'] = self.userpwDict

        self.gzs_objectid = self.__get_gzsobjectid_from_task()             
        self.task_config['gzs_objectid'] = self.gzs_objectid

        self.gpr, self.jahr, self.version, self.zeitstand, self.rolle_freigabe = self.__get_gprinfo_from_dd()
        self.task_config['gpr'] = self.gpr
        self.task_config['zeitstand'] = self.zeitstand
        self.task_config['zeitstand_jahr'] = self.jahr
        self.task_config['zeitstand_version'] = self.version
        self.task_config['rolle'] = self.rolle_freigabe

        ebeVecList, ebeRasList, ebeCacheList = self.__get_ebeinfo_from_dd()
        ebeVecList.extend(self.__get_wtb_dd())
        self.task_config['vektor_ebenen'] = ebeVecList
        self.task_config['raster_ebenen'] = ebeRasList
        self.task_config['cache_ebenen'] = ebeCacheList

        self.zielDict = self.__define_quelle_ziel_begleitdaten()
        self.task_config['ziel'] = self.zielDict

        self.task_config['mxd'] = [self.__get_mxd_dd("DE"), self.__get_mxd_dd("FR")]

        self.task_config['legende'] = self.__get_leg_dd()

        self.task_config['style'], self.task_config['font'] = self.__get_fak_begleitdaten()

        self.task_config['zusatzdaten'] = self.__get_fak_zusatzdaten()

        self.task_config['oereb'] = self.__get_oereb_infos()

        # Verschiedene Parameter direkt aus der Config übernommen
        self.task_config['quelle_begleitdatenraster'] = os.path.join(self.general_config['quelle_begleitdaten'], self.gpr, 'work', 'symbol','Rasterdataset')
        self.task_config['default_tolerance'] = self.general_config['default_tolerance']
        self.task_config['default_resolution'] = self.general_config['default_resolution']
        self.task_config['spatial_reference'] = self.general_config['spatial_reference']
        self.task_config['db_vek1_pg'] = self.general_config['connection_infos']['db']['vek1']['pg_db']
        self.task_config['db_vek2_pg'] = self.general_config['connection_infos']['db']['vek2']['pg_db']
        self.task_config['db_team_pg'] = self.general_config['connection_infos']['db']['team']['pg_db']
        self.task_config['port_pg'] = self.general_config['connection_infos']['db']['vek1']['pg_port']

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
