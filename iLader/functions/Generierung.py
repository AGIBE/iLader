# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import os
import json
import cx_Oracle as ora

class Generierung(TemplateFunction):
    '''
    Sammelt sämtliche benötigten Informationen zusammen aus:
    - DataDictionary
    - General Config
    - GeoDBProzess
    Die Informationen werden in die task_config geschrieben.
    '''


    def __init__(self, logger, task_config, general_config):
        '''
        Constructor
        :param logger: vom Usecase initialisierter logger (logging.logger)
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = u"Generierung"
        TemplateFunction.__init__(self, logger, task_config)
        
        self.logger = logger
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
        self.sql_name = sql_name
        self.instance = instance
        self.usergroup = usergroup
        self.username = self.general_config['users'][self.usergroup]['username']
        self.password = self.general_config['users'][self.usergroup]['password']
        self.db = self.general_config['instances'][self.instance]
        self.logger.info(u"Username: " + self.username)
        self.logger.info(u"Verbindung herstellen mit der Instanz " + self.db)
        self.connection = ora.connect(self.username, self.password, self.db)
        self.logger.info(u"Es wird folgendes encoding verwendet:")
        self.logger.info(self.connection.encoding)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.sql_name)
        self.result = self.cursor.fetchall()
        self.connection.close()    
    
    def __get_importe_dd(self):
        #TODO: Tabelle tb_importe_geodb erstellen
        #TODO: self.sql_dd_importe = "select * from geodb_dd.tb_importe_geodb"
        #TODO: self.__db_connect('dd_connection', self.sql_dd_importe)
        #TODO: taskid aus tb_importe_geodb übergeben und gzs_objectid übernehmen
        self.gzs_objectid = '157675'

    
    def __get_gpr_info(self):
        self.sql_dd_gpr = "SELECT a.gpr_bezeichnung, b.gzs_jahr, b.gzs_version, a.gpr_viewer_freigabe from geodb_dd.tb_geoprodukt_zeitstand b join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"
        self.__db_connect('team', 'geodb_dd', self.sql_dd_gpr)
        for row in self.result:
            self.gpr = row[0].decode('cp1252')
            self.jahr = str(row[1]).decode('cp1252')
            self.version = str(row[2]).decode('cp1252')
            self.version = self.version.zfill(2)
            self.zeitstand = self.jahr + "_" + self.version
            self.rolle_freigabe = row[3].decode('cp1252')
    
    def __get_ebe_dd(self):
        self.sql_dd_ebe = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, g.dat_bezeichnung_de from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"   
        self.__db_connect('team', 'geodb_dd', self.sql_dd_ebe)
        for row in self.result:
            self.logger.info(row)
            ebeVecDict = {}
            ebeRasDict = {}
            gpr = row[0].decode('cp1252')
            ebe = row[1].decode('cp1252')
            jahr = str(row[2]).decode('cp1252')
            version = str(row[3]).decode('cp1252')
            version = version.zfill(2)
            datentyp = row[4].decode('cp1252')            
            zeitstand = jahr + "_" + version
            gpr_ebe = str(gpr) + "_" + str(ebe)
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
            if datentyp != 'Rastermosaik' and datentyp != 'Rasterkatalog':
                self.sql_ind_gdbp = "SELECT b.felder, b." + '"unique"' + " from gdbp.index_attribut b join gdbp.geoprodukte a on b.id_geoprodukt = a.id_geoprodukt where a.code = '" + gpr + "' and b.ebene = '" + ebe + "'"
                self.__db_connect('work', 'gdbp', self.sql_ind_gdbp)
                self.indList = []
                for row in self.result:
                    indDict = {}
                    ind_attr = row[0].decode('cp1252')
                    indextyp = str(row[1]).decode('cp1252')
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
            elif datentyp == 'Rastermosaik': # später Rasterdataset
                ebeRasDict['datentyp'] = datentyp
                ebeRasDict['gpr_ebe'] = gpr_ebe
                ebeRasDict['quelle'] = quelle
                ebeRasDict['ziel_ras1']= ziel_ras1_akt
                ebeRasDict['ziel_ras1_zs']= ziel_ras1_zs
                self.ebeRasList.append(ebeRasDict)
            elif datentyp == 'Mosaicdataset': # TODO neuer Datentyp MosaicDataset einfügen (hier Rasterkatalog nur zu Testzwecken
                #TODOself.sql_raster_properties = "SELECT * from gdbp.raster_xy a where a.gpr = SWISSI"
                self.__db_connect('work', 'gdbp', self.sql_raster_properties)
                ebeRasDict['datentyp'] = datentyp
                ebeRasDict['gpr_ebe'] = gpr_ebe
                #TODO: Quelle von MosaicDatasets festlegen (in erweiterten Tabellen gdbp.info_rastermosaic ebeRasDict['quelle'] = u'noch offen' / 
                # MD: ebeRasDict['quelle'] = os.path.join(self.general_config['quelle_begleitdaten_work'], self.general_config['raster']['quelle_rasterkacheln'], self.general_config['raster']['raster_md'])
                # RD: ebeRasDict['quelle'] = os.path.join(self.general_config['quelle_begleitdaten_work'], self.general_config['raster']['quelle_rasterkacheln'], self.general_config['raster']['raster_rd'])
                ebeRasDict['ziel_ras2'] = ziel_ras2
                self.ebeRasList.append(ebeRasDict)          
                         
                
    def __get_leg_dd(self, create_zs):
        self.create_zs = create_zs
        self.sql_dd_ebe = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, f.leg_bezeichnung, h.spr_kuerzel from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid JOIN geodb_dd.tb_legende f on f.ezs_objectid = d.ezs_objectid JOIN geodb_dd.tb_sprache h on h.spr_objectid = f.spr_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"   
        self.__db_connect('team', 'geodb_dd', self.sql_dd_ebe)
        for row in self.result:
            self.legDict = {}
            self.logger.info(u'Legendendetails')
            self.logger.info(row)
            self.gpr = str(row[0]).decode('cp1252')
            self.ebe = str(row[1]).decode('cp1252')
            self.jahr = str(row[2]).decode('cp1252')
            self.version = str(row[3]).decode('cp1252')
            self.version = self.version.zfill(2)           
            self.zeitstand = self.jahr + "_" + self.version
            self.leg = str(row[4]).decode('cp1252')
            self.spr = str(row[5]).decode('cp1252')
            if self.create_zs == "True":
                self.symbol_name = self.gpr + "_" + self.ebe + "_" + self.zeitstand + "_" + self.leg + "_" + self.spr + ".lyr"
            if self.create_zs == "False":
                self.symbol_name = self.gpr + "_" + self.ebe + "_" + self.leg + "_" + self.spr + ".lyr"
            self.logger.info(self.symbol_name)
            self.quelle_symbol =  os.path.join(self.quelle_begleitdaten_symbol, self.symbol_name)
            self.ziel_symbol = os.path.join(self.ziel_begleitdaten_symbol, self.symbol_name)
            self.legDict['name'] = self.symbol_name
            self.legDict['quelle'] = self.quelle_symbol
            self.legDict['ziel'] = self.ziel_symbol
            self.legList.append(self.legDict)

    
    def __get_mxd_dd(self, create_zs, lang):
            self.mxdDict = {}
            self.create_zs = create_zs
            self.lang = lang
            if self.create_zs == "False":
                self.mxd_lang = self.gpr + "_" + self.gpr + "_" + self.lang + ".mxd"
                self.quelle_mxd_lang = os.path.join(self.quelle_begleitdaten_mxd, self.mxd_lang)
            if self.create_zs == "True":
                self.mxd_lang = self.gpr + "_" + self.zeitstand + "_" + self.gpr + "_" + self.lang + ".mxd"
            self.quelle_mxd_lang = os.path.join(self.quelle_begleitdaten_mxd, self.mxd_lang)                
            self.ziel_mxd_lang = os.path.join(self.ziel_begleitdaten_mxd, self.mxd_lang)
            self.mxdDict['name'] = self.mxd_lang
            self.mxdDict['quelle'] = self.quelle_mxd_lang
            self.mxdDict['ziel'] = self.ziel_mxd_lang             
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
                    styleDict['ziel'] = os.path.join(self.ziel_begleitdaten_symbol, file)
                    self.styleList.append(styleDict)
                elif file.endswith('.ttf') or file.endswith('.TTF'):
                    fontDict['name'] = file
                    fontDict['quelle'] = os.path.join(self.quelle_begleitdaten_symbol, file)
                    fontDict['ziel'] = os.path.join(self.ziel_begleitdaten_symbol, file)
                    self.fontList.append(fontDict)
            for dir in dirs:
                zusatzDict = {}
                if dir == "zusatzdaten":
                    zusatzDict['quelle'] = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_zusatzdaten'])
                    zusatzDict['ziel'] = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_zusatzdaten'])
                    self.zusatzList.append(zusatzDict)         

    def __define_quelle_ziel_begleitdaten(self):
            zielDict = {}
            self.quelle_begleitdaten_gpr = os.path.join(self.general_config['quelle_begleitdaten'], self.gpr, self.general_config['quelle_begleitdaten_work'])
            self.quelle_begleitdaten_mxd = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_mxd'])
            self.quelle_begleitdaten_symbol = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_symbol'])
            self.quelle_begleitdaten_zusatzdaten = os.path.join(self.quelle_begleitdaten_gpr, self.general_config['quelle_begleitdaten_zusatzdaten'])
            self.ziel_begleitdaten_gpr = os.path.join(self.general_config['ziel_begleitdaten'], self.gpr)
            self.ziel_begleitdaten_mxd = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_mxd'])
            self.ziel_begleitdaten_symbol = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_symbol'])
            self.ziel_begleitdaten_zusatzdaten = os.path.join(self.ziel_begleitdaten_gpr, self.general_config['ziel_begleitdaten_zusatzdaten'])
            zielDict['ziel_begleitdaten_gpr'] = self.ziel_begleitdaten_gpr
            zielDict['ziel_begleitdaten_mxd'] = self.ziel_begleitdaten_mxd
            zielDict['ziel_begleitdaten_symbol'] = self.ziel_begleitdaten_symbol
            zielDict['ziel_begleitdaten_zusatzdaten'] = self.ziel_begleitdaten_zusatzdaten
            self.zielList.append(zielDict)
      
         
    def __get_wtb_dd(self):
        self.sql_dd_wtb = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, e.wtb_bezeichnung from geodb_dd.tb_wertetabelle e join geodb_dd.tb_ebene_zeitstand d on e.ezs_objectid = d.ezs_objectid join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"
        self.__db_connect('team', 'geodb_dd', self.sql_dd_wtb)
        for row in self.result:
            wtbDict = {}
            self.logger.info(row)
            gpr = row[0].decode('cp1252')
            self.logger.info(type(gpr))
            wtb = row[4].decode('cp1252')
            jahr = str(row[2]).decode('cp1252')
            version = str(row[3]).decode('cp1252')
            version = version.zfill(2)
            zeitstand = jahr + "_" + version
            gpr_wtb = str(gpr) + "_" + str(wtb)            
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
                indextyp = str(row[1]).decode('cp1252')
                if indextyp == "1":
                    ind_unique = "True"
                elif indextyp == "2":
                    ind_unique = "False"
                indDict['attribute'] = ind_attr
                indDict['unique'] = ind_unique            
                self.indList.append(indDict)
            wtbDict['indices'] = self.indList
            wtbDict['datentyp']= u"Tabelle"
            wtbDict['gpr_ebe'] = gpr_wtb
            wtbDict['quelle'] = quelle
            wtbDict['ziel_vek1'] = ziel_vek1
            wtbDict['ziel_vek2'] = ziel_vek2
            wtbDict['ziel_vek3'] = ziel_vek3
            self.ebeVecList.append(wtbDict)
               
    def __define_qs(self):
        qsDict = {}
        #TODO: self.sql_dd_importe = "select * from geodb_dd.tb_importe_geodb"
        #TODO: self.__db_connect('dd_connection', self.sql_dd_importe)
        #TODO: dma_erlaubt für qs auslesen und 'dma_erlaubt' übergeben
        qsDict['dma_erlaubt'] = u'false'
        qsDict['checkskript_passed'] = u'undefined'
        qsDict['deltachecker_passed'] = u'undefined'
        qsDict['qa_framework_passed'] = u'undefined'
        qsDict['qs_gesamt_passed'] = u'undefined'
        self.qsList.append(qsDict)   
          
            
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
        self.sde_conn_team_oereb = os.path.join(self.sde_connection_directory, 'team_oereb.sde')
        self.sde_conn_vek1_oereb = os.path.join(self.sde_connection_directory, 'vek1_oereb.sde')
        self.sde_conn_vek2_oereb = os.path.join(self.sde_connection_directory, 'vek2_oereb.sde')      
        self.connDict['sde_conn_team_dd'] = self.sde_conn_team_dd
        self.connDict['sde_conn_vek1'] = self.sde_conn_vek1
        self.connDict['sde_conn_vek2'] = self.sde_conn_vek2
        self.connDict['sde_conn_vek3'] = self.sde_conn_vek3
        self.connDict['sde_conn_ras1'] = self.sde_conn_ras1
        self.connDict['sde_conn_ras2'] = self.sde_conn_ras2
        self.connDict['sde_conn_norm'] = self.sde_conn_norm
        self.connDict['sde_conn_team_oereb'] = self.sde_conn_team_oereb
        self.connDict['sde_conn_vek1_oereb'] = self.sde_conn_vek1_oereb
        self.connDict['sde_conn_vek2_oereb'] = self.sde_conn_vek2_oereb
        self.connList.append(self.connDict)
        self.schemaDict = {}
        self.schema_geodb = self.general_config['users']['geodb']['schema']
        self.schema_geodb_dd = self.general_config['users']['geodb_dd']['schema']
        self.schema_norm = self.general_config['users']['norm']['schema']
        self.schema_oereb = self.general_config['users']['oereb']['schema']
        self.schema_gdbp = self.general_config['users']['gdbp']['schema']
        self.schemaDict['geodb'] = self.schema_geodb
        self.schemaDict['geodb_dd'] = self.schema_geodb_dd
        self.schemaDict['norm'] = self.schema_norm
        self.schemaDict['oereb'] = self.schema_oereb
        self.schemaDict['gdbp'] = self.schema_gdbp
        self.schemaList.append(self.schemaDict) 

                
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        #Diverse Einträge im task_config generieren
        if not self.task_config.has_key("ausgefuehrte_funktionen"):
            self.task_config['ausgefuehrte_funktionen'] = []
       
        self.connList = []
        self.schemaList = []
        self.ebeVecList = []
        self.ebeRasList = []
        self.legList = []
        self.mxdList = []
        self.styleList = []
        self.fontList = []
        self.zusatzList = []
        self.zielList = []
        self.qsList = []
        self.__define_connections()               
        self.__get_importe_dd()
        self.__get_gpr_info()
        self.__get_ebe_dd()
        self.__get_wtb_dd()
        self.__define_quelle_ziel_begleitdaten()
        self.__get_mxd_dd("False", "DE")
        self.__get_mxd_dd("False", "FR")
        self.__get_mxd_dd("True", "DE")
        self.__get_mxd_dd("True", "FR")
        self.__get_leg_dd("True")
        self.__get_leg_dd("False")
        self.__get_fak_begleitdaten()
        self.__define_qs()
        
        self.task_config['connections'] = self.connList
        self.task_config['schema'] = self.schemaList
        self.task_config['gpr'] = self.gpr
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
        self.task_config['qs'] = {'dma_erlaubt': u'false', 'checkskript_passed': u'undefined', 'deltachecker_passed': u'undefined', 'qa_framework_passed': u'undefined', 'qs_gesamt_passed': u'undefined'}
        self.task_config['zusatzdaten'] = self.zusatzList
        self.task_config['ziel'] = self.zielList
        self.task_config['qs'] = self.qsList
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
                
