# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import iLader.helpers.OracleHelper
import iLader.helpers.Helpers
import arcpy
import os

class ViewsVek2(TemplateFunction):
    '''
    Erstellt für sämtliche Vektor-Ebenen in VEK2 Views, in denen die Wertetabellen eingebunden sind
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["vektor_ebenen"]``
    
    Nach dem Kopiervorgang setzt die Funktion auch noch die korrekten Berechtigungen d.h.
    sie vergibt SELECT-Rechte an eine Rolle. Die Rolle ist in task_config abgelegt:
    
    - ``task_config["rolle"]``

    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "ViewsVek2"
        TemplateFunction.__init__(self, task_config)

        # Der Zugriff auf das Config-File ist für die Verbindungs-Infos notwendig.
        self.general_config = iLader.helpers.Helpers.init_generalconfig()
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()

    def __getColumns(self, tablename, schema):
        columns = []
        column_sql = "select column_name from all_tab_columns where owner='" + schema + "' and table_name='" + tablename + "' ORDER BY COLUMN_ID"
        
        column_results = iLader.helpers.OracleHelper.readOracleSQL(self.general_config['instances']['vek2'], self.general_config['users']['geodb']['username'], self.general_config['users']['geodb']['password'], column_sql)
        
        for c in column_results:
            columns.append(c[0])
                
        return columns        

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("Views in VEK2 werden erstellt.")
        rolle = self.task_config['rolle']
        schema = self.task_config['schema']['geodb']

        for ebene in self.task_config['vektor_ebenen']:
            view_name = ebene['gpr_ebe'] + "_VW"
            view_name_vek2 = os.path.join(self.task_config['connections']['sde_conn_vek2'], view_name)
            if arcpy.Exists(view_name_vek2):
                self.logger.info("View existiert bereits. Er wird gelöscht.")
                self.logger.info(view_name_vek2)
                arcpy.Delete_management(view_name_vek2)

            if ebene['datentyp'] not in ['Wertetabelle', 'Annotation']:
                self.logger.info("Für Ebene " + ebene['gpr_ebe'] + " wird ein View erstellt.")
                wertetabellen = ebene['wertetabellen']
                
                self.logger.info("View-Name: " + view_name)
                
                ebene_fullname = schema + "." + ebene['gpr_ebe']
                
                full_columns = []
                join_sql = ""

                # Es gibt Fälle, in denen die gleiche Wertetabelle mehrfach
                # pro Feature Classes angehängt wird. In diesem Fall sind die
                # Attributnamen nicht mehr eindeutig. Daher muss ab der zweiten
                # identischen Wertetabelle ein anderes Präfix genommen werden.
                # Dazu braucht es eine Hilfsliste mit den bereits verarbeiteten
                # Wertetabellen.
                processed_wertetabellen = []
                
                for c in self.__getColumns(ebene['gpr_ebe'], schema):
                    # Jede Spalte der Feature Class wird im View auftauchen
                    full_columns.append(ebene_fullname + "." + c)
                    
                    # Prüfen, ob an dieser Spalte eine Wertetabelle angehängt wird.
                    for w in wertetabellen:
                        if w['wtb_jointype'] not in ['Relate']:
                            wtb_name = self.task_config['gpr'] + "_" + w['wtb_code']
                            wtb_fullname = schema + "." + wtb_name
                            if c == w['wtb_foreignkey']:
                                if w['wtb_jointype'].lower() == 'esrileftouterjoin':
                                    join = " LEFT OUTER JOIN"
                                elif w['wtb_jointype'].lower() == 'esrileftinnerjoin':
                                    join = " INNER JOIN"
                                join_sql += join + " " + wtb_fullname + " ON " + ebene_fullname + "." + w['wtb_foreignkey'] + "=" + wtb_fullname + "." + w['wtb_primarykey'] + " "
                                wtb_columns = self.__getColumns(wtb_name, schema)
                                
                                # Wird die gleiche Wertetabelle mehr als einmal angehängt,
                                # muss sie ab dem zweiten Mal ein anderes Prefix haben.
                                # Das wird hier geprüft.
                                counter = ""
                                if wtb_name in processed_wertetabellen:
                                    processed_wertetabellen.append(wtb_name)
                                    counter = unicode(processed_wertetabellen.count(wtb_name))
                                else:
                                    processed_wertetabellen.append(wtb_name)
                                
                                for wc in wtb_columns:
                                    # Das OBJECTID-Feld der Wertetabelle soll nicht im View erscheinen (überflüssig)
                                    # Der PrimaryKey der Wertetabelle soll nicht im View erscheinen (redundant)
                                    if wc != "OBJECTID" and wc != w['wtb_primarykey']:
                                            full_columns.append(wtb_fullname + "." + wc + " AS " + w['wtb_code'] + counter + "_" + wc)
                        else:
                            self.logger.info("Der Join zur Wertetabelle " + w['wtb_code'] + " ist ein Relate.")
                            self.logger.info("Er wird nicht in den View integriert.")
                    
                view_sql = "CREATE OR REPLACE VIEW " + view_name + " AS SELECT " + ",".join(full_columns) + " FROM " + ebene_fullname + join_sql + " WITH READ ONLY"
                grant_sql = "GRANT SELECT ON " + view_name + " TO " + rolle
                
                self.logger.info("View-SQL: ")
                self.logger.info(view_sql)
                iLader.helpers.OracleHelper.writeOracleSQL(self.general_config['instances']['vek2'], self.general_config['users']['geodb']['username'], self.general_config['users']['geodb']['password'], view_sql)
                self.logger.info("Rechte für den View " + view_name + " werden gesetzt.")
                self.logger.info(grant_sql)
                iLader.helpers.OracleHelper.writeOracleSQL(self.general_config['instances']['vek2'], self.general_config['users']['geodb']['username'], self.general_config['users']['geodb']['password'], grant_sql)

            elif ebene['datentyp'] == 'Annotation':
                self.logger.info("Für die Ebene " + ebene['gpr_ebe'] + " wird kein View erstellt, weil sie eine Annotation ist. Sie wird stattdessen kopiert.")
                self.logger.info("Quelle: " + ebene['ziel_vek2'])
                self.logger.info("Ziel: " + view_name_vek2)
                arcpy.Copy_management(ebene['ziel_vek2'], view_name_vek2)
                arcpy.ChangePrivileges_management(view_name_vek2, rolle, "GRANT")
            else:
                self.logger.info("Für die Ebene " + ebene['gpr_ebe'] + " wird kein View erstellt, weil sie eine Wertetabelle ist.")
            
            self.logger.info("Für die Ebene " + ebene['gpr_ebe'] + " wurde der View erstellt.")    
            
        self.logger.info("Alle Views in Vek2 wurden erstellt.")        
       
        self.finish()