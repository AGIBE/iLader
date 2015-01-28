# -*- coding: utf-8 -*-
'''
Created on 09.01.2015

@author: Peter Schär
'''
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
        self.gzs_objectid = '157675'

    
    def __get_gpr_info(self):
        self.sql_dd_gpr = "SELECT a.gpr_bezeichnung, b.gzs_jahr, b.gzs_version, a.gpr_viewer_freigabe from geodb_dd.tb_geoprodukt_zeitstand b join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"
        self.__db_connect('team', 'geodb_dd', self.sql_dd_gpr)
        for row in self.result:
            self.gpr = row[0].decode('cp1252')
            self.jahr = str(row[1]).decode('cp1252')
            self.version = str(row[2]).decode('cp1252')
            self.zeitstand = self.jahr + "_" + self.version
            self.rolle_freigabe = row[3].decode('cp1252')
    
    def __get_ebe_dd(self):
        self.sql_dd_ebe = "SELECT a.gpr_bezeichnung, c.ebe_bezeichnung, b.gzs_jahr, b.gzs_version, g.dat_bezeichnung_de from geodb_dd.tb_ebene_zeitstand d join geodb_dd.tb_ebene c on d.ebe_objectid = c.ebe_objectid join geodb_dd.tb_geoprodukt_zeitstand b on d.gzs_objectid = b.gzs_objectid join geodb_dd.tb_geoprodukt a on b.gpr_objectid = a.gpr_objectid join geodb_dd.tb_datentyp g on c.dat_objectid = g.dat_objectid where b.gzs_objectid = '" + self.gzs_objectid + "'"   
        self.__db_connect('team', 'geodb_dd', self.sql_dd_ebe)
        for row in self.result:
            ebeDict = {}
            gpr = row[0].decode('cp1252')
            ebe = row[1].decode('cp1252')
            jahr = str(row[2]).decode('cp1252')
            version = str(row[3]).decode('cp1252')
            datentyp = row[4].decode('cp1252')
            zeitstand = jahr + "_" + version
            gpr_ebe = str(gpr) + "_" + str(ebe)
            quelle_schema_gpr_ebe = self.schema_norm + "_" + gpr_ebe
            quelle = os.path.join(self.sde_conn_norm + quelle_schema_gpr_ebe)
            ziel_schema_gpr_ebe = self.schema_geodb + "_" + gpr_ebe
            ziel_schema_gpr_ebe_zs = ziel_schema_gpr_ebe + "_" + zeitstand     
            ziel_vek1 = os.path.join(self.sde_conn_vek1, ziel_schema_gpr_ebe)
            ziel_vek2 = os.path.join(self.sde_conn_vek2, ziel_schema_gpr_ebe)
            ziel_vek3 = os.path.join(self.sde_conn_vek3, ziel_schema_gpr_ebe_zs)
            ebeDict['datentyp']= datentyp
            ebeDict['gpr_ebe'] = gpr_ebe
            ebeDict['quelle'] = quelle
            ebeDict['ziel_vek1'] = ziel_vek1
            ebeDict['ziel_vek2'] = ziel_vek2
            ebeDict['ziel_vek3'] = ziel_vek3
            self.ebeList.append(ebeDict)
        
            
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
            quelle_schema_gpr_wtb = self.schema_norm + "_" + gpr_wtb
            quelle = os.path.join(self.sde_conn_norm + quelle_schema_gpr_wtb)
            ziel_schema_gpr_wtb = self.schema_geodb + "_" + gpr_wtb
            ziel_schema_gpr_wtb_zs = ziel_schema_gpr_wtb + "_" + zeitstand                
            ziel_vek1 = os.path.join(self.sde_conn_vek1, ziel_schema_gpr_wtb)
            ziel_vek2 = os.path.join(self.sde_conn_vek2, ziel_schema_gpr_wtb)
            ziel_vek3 = os.path.join(self.sde_conn_vek3, ziel_schema_gpr_wtb_zs)
            wtbDict['datentyp']= u"Tabelle"
            wtbDict['gpr_ebe'] = gpr_wtb
            wtbDict['quelle'] = quelle
            wtbDict['ziel_vek1'] = ziel_vek1
            wtbDict['ziel_vek2'] = ziel_vek2
            wtbDict['ziel_vek3'] = ziel_vek3
            self.ebeList.append(wtbDict)
              
                
    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        #Diverse Einträge im task_config generieren
        if not self.task_config.has_key("ausgefuehrte_funktionen"):
            self.task_config['ausgefuehrte_funktionen'] = []

        self.config_secret = os.environ['GEODBIMPORTSECRET']
        self.sde_connection_directory = os.path.join(self.config_secret, 'connections')
        self.sde_conn_vek1 = os.path.join(self.sde_connection_directory, 'vek1.sde')
        self.sde_conn_vek2 = os.path.join(self.sde_connection_directory, 'vek2.sde')
        self.sde_conn_vek3 = os.path.join(self.sde_connection_directory, 'vek3.sde')
        self.sde_conn_norm = os.path.join(self.sde_connection_directory, 'norm.sde')
        self.schema_geodb = self.general_config['users']['geodb']['schema']
        self.schema_norm = self.general_config['users']['norm']['schema']
       
        self.ebeList = []               
        self.__get_importe_dd()
        self.__get_gpr_info()
        self.__get_ebe_dd()
        self.__get_wtb_dd()
        self.task_config['vektor_ebenen']= self.ebeList
        self.task_config['gpr'] = self.gpr
        self.task_config['zeitstand'] = self.zeitstand
        self.task_config['zeitstand_jahr'] = self.jahr
        self.task_config['zeitstand_version'] = self.version
        self.task_config['rolle'] = self.rolle_freigabe
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
                
