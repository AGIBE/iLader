# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import AGILib
import arcpy
import os
from iLader.helpers.Helpers import prepare_fme_log
from iLader.helpers.Helpers import create_dummy
from iLader.helpers.Helpers import delete_dummy


class KopieVek2Ersatz_PG(TemplateFunction):
    '''
    Kopiert sämtliche Vektorebenen aus der Instanz TEAM in die Instanz vek2 (PostgreSQL). Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz vek2 sind die Ebenen bereits vorhanden und müssen vorgängig
    gelöscht werden.
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["vektor_ebenen"]``
    
    Nach dem Kopiervorgang setzt die Funktion auch noch die korrekten Berechtigungen d.h.
    sie vergibt SELECT-Rechte an eine Rolle. Die Rolle ist in task_config abgelegt:
    
    - ``task_config["rolle"]``
    
    Auf das explizite Berechnen des räumlichen Indexes wird verzichtet.
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "KopieVek2Ersatz_PG"
        TemplateFunction.__init__(self, task_config, general_config)

        if self.name in self.task_config['ausgefuehrte_funktionen'
                                         ] and self.task_config[
                                                 'resume']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgefuehrt.")
            self.start()
            self.__execute()

    def __execute(self):
        '''
        Führt den eigentlichen Funktionsablauf aus
        '''
        rolle = self.task_config['rolle']
        db = self.general_config['connections']['VEK2_GEODB_PG'].db
        port = self.general_config['connections']['VEK2_GEODB_PG'].port
        host = self.general_config['connections']['VEK2_GEODB_PG'].host
        db_user = self.general_config['connections']['VEK2_GEODB_PG'].username
        pw = self.general_config['connections']['VEK2_GEODB_PG'].password
        schema = db_user
        source_sde = self.general_config['connection_files']['TEAM_NORM_ORA']
        fme_script = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..')
        ) + "\\helpers\\" + "EsriGeodatabase2PostGIS.fmw"

        # Jede Ebene durchgehen
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']
            source_table = source.rsplit('\\', 1)[1]
            table = ebene['ziel_vek2'].rsplit('\\', 1)[1]
            ebename = ebene['gpr_ebe'].lower()
            dummy_entry = False

            self.logger.info("Ebene " + ebename + " wird nach vek2 kopiert.")
            self.logger.info("Quelle: " + source)
            self.logger.info("Ziel: " + host + "/" + db + " " + table)

            # Prüfen, ob es eine Featureclass oder eine Standalone-Tabelle ist
            tabellentyp = "featureclass"
            if ebene['datentyp'] in ('Tabelle', 'unbekannt', 'Wertetabelle'):
                tabellentyp = "table"

            # Pruefen ob es die source Tabelle gibt
            if not arcpy.Exists(source):
                # Existiert die Quell-Ebene nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Quell-Ebene " + source + " existiert nicht!")
                raise Exception

            # Prüfen ob die source Tabelle leer ist
            count_source = int(arcpy.GetCount_management(source)[0])
            if count_source == 0:
                self.logger.info(
                        "Quell-Ebene " + source +
                        " ist leer. Es wird ein Dummy-Eintrag erstellt."
                )
                create_dummy(source)
                dummy_entry = True

            # Eine Liste der Attribute mit Typ Date erstellen (FME braucht diese Info, damit leere Datumsfelder fuer Postgres richtig gesetzt werden koennen)
            datefields = arcpy.ListFields(source, field_type='Date')
            dfield = None
            for datefield in datefields:
                if dfield is None:
                    dfield = datefield.name
                else:
                    dfield = dfield + ' ' + datefield.name

            # Daten kopieren
            # Copy-Script
            fme_logfile = prepare_fme_log(
                    fme_script, (self.task_config['log_file']).rsplit('\\',
                                                                      1)[0]
            )
            # Daher muessen workspace und parameters umgewandelt werden!
            # Gibt es die Ziel-Ebene bereits, muss sie geloescht werden (TABLE_HANDLING)
            fme_parameters = {
                    'TABELLEN': source_table,
                    'POSTGIS_DB': db,
                    'POSTGIS_HOST': host,
                    'POSTGIS_PORT': port,
                    'POSTGIS_USER': db_user,
                    'POSTGIS_PASSWORD': pw,
                    'SCHEMA_NAME': schema,
                    'LOGFILE': fme_logfile,
                    'INPUT_SDE': source_sde,
                    'TABLE_HANDLING': "DROP_CREATE",
                    'DATEFIELDS': dfield,
                    'TABELLENTYP': tabellentyp
            }

            fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=fme_parameters, fme_logfile=fme_logfile, fme_logfile_archive=False)
            fmerunner.run()
            if fmerunner.returncode != 0:
                self.logger.error("FME-Script %s abgebrochen." % (fme_script))
                raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))

            # Dummy-Eintrag entfernen
            if dummy_entry:
                self.logger.info("Dummy-Eintrag wird wieder entfernt.")
                delete_dummy(source, table, self.general_config['connections']['VEK2_GEODB_PG'])

            # Berechtigungen setzen
            self.logger.info(
                    "Berechtigungen für Ebene " + table +
                    " wird gesetzt: Rolle " + rolle
            )
            grant_sql = 'GRANT SELECT ON ' + table + ' TO ' + rolle
            self.general_config['connections']['VEK2_GEODB_PG'].db_write(grant_sql)

            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            count_source = int(arcpy.GetCount_management(source)[0])
            self.logger.info(
                    "Anzahl Objekte in Quell-Ebene: " + unicode(count_source)
            )
            count_target_sql = 'SELECT COUNT(*) FROM %s' % (table)
            count_target_result = self.general_config['connections']['VEK2_GEODB_PG'].db_read(count_target_sql)
            count_target = count_target_result[0][0]
            self.logger.info(
                    "Anzahl Objekte in Ziel-Ebene: " + unicode(count_target)
            )

            if count_source != int(count_target):
                self.logger.error(
                        "Anzahl Objekte in Quelle und Ziel unterschiedlich!"
                )
                raise Exception
            else:
                self.logger.info("Anzahl Objekte in Quelle und Ziel identisch!")

            self.logger.info("Ebene " + ebename + " wurde kopiert")

        self.logger.info("Alle Ebenen wurden kopiert.")
        self.finish()