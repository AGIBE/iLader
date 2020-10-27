# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
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

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "ViewsVek2"
        TemplateFunction.__init__(self, task_config, general_config)

        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['resume']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgeführt.")
            self.start()
            self.__execute()

    def __getColumns(self, tablename, schema, connection):
        column_sql = "select column_name from user_tab_columns where table_name='%s' ORDER BY COLUMN_ID" % (tablename)
        self.logger.info(column_sql)
        column_results = connection.db_read(column_sql)
        return [c[0] for c in column_results]

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("Views in VEK2 werden erstellt.")
        target_connection = self.general_config['connections']['VEK2_GEODB_ORA']
        rolle = self.task_config['rolle']
        schema = target_connection.username

        for ebene in self.task_config['vektor_ebenen']:
            view_name = ebene['gpr_ebe'] + "_VW"
            view_name_vek2 = os.path.join(self.general_config['connection_files']['VEK2_GEODB_ORA'], view_name)
            if arcpy.Exists(view_name_vek2):
                self.logger.info("View existiert bereits. Er wird gelöscht.")
                self.logger.info(view_name_vek2)
                arcpy.Delete_management(view_name_vek2)

            if ebene['datentyp'] not in ['Wertetabelle', 'Annotation']:
                self.logger.info("Für Ebene %s wird ein View erstellt." % (ebene['gpr_ebe']))
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
                
                for c in self.__getColumns(ebene['gpr_ebe'], schema, target_connection):
                    # Jede Spalte der Feature Class wird im View auftauchen
                    full_columns.append(ebene_fullname + "." + c)
                    
                    # Prüfen, ob an dieser Spalte eine Wertetabelle angehängt wird.
                    for w in wertetabellen:
                        # Relate-Wertetabellen werden ignoriert
                        if w['wtb_jointype'] not in ['Relate']:
                            wtb_name = self.task_config['gpr'] + "_" + w['wtb_code']
                            wtb_fullname = schema + "." + wtb_name
                            if c == w['wtb_foreignkey']:
                                if w['wtb_jointype'].lower() == 'esrileftouterjoin':
                                    join = " LEFT OUTER JOIN"
                                elif w['wtb_jointype'].lower() == 'esrileftinnerjoin':
                                    join = " INNER JOIN"
                                join_sql += join + " " + wtb_fullname + " ON " + ebene_fullname + "." + w['wtb_foreignkey'] + "=" + wtb_fullname + "." + w['wtb_primarykey'] + " "
                                wtb_columns = self.__getColumns(wtb_name, schema, target_connection)
                                
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
                            self.logger.info("Der Join zur Wertetabelle %s ist ein Relate." % (w['wtb_code']))
                            self.logger.info("Er wird nicht in den View integriert.")
                    
                view_sql = "CREATE OR REPLACE VIEW " + view_name + " AS SELECT " + ",".join(full_columns) + " FROM " + ebene_fullname + join_sql + " WITH READ ONLY"
                grant_sql = "GRANT SELECT ON " + view_name + " TO " + rolle
                
                self.logger.info("View-SQL: ")
                self.logger.info(view_sql)
                target_connection.db_write(view_sql)
                self.logger.info("Rechte für den View " + view_name + " werden gesetzt.")
                self.logger.info(grant_sql)
                target_connection.db_write(grant_sql)

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