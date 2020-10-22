# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import iLader.helpers.Helpers
import AGILib
import arcpy
import os

class KopieVek1Ersatz_PG(TemplateFunction):
    '''
    Kopiert saemtliche Vektorebenen aus der Instanz TEAM in die Instanz vek1 (PostgreSQL). Folgende Typen
    werden kopiert:
    
    - Vektor-FeatureClasses
    - Tabellen (Standalone oder Werte-)
    - Annotations
    
    In der Zielinstanz vek1 sind die Ebenen bereits vorhanden. Da keine Datenmodellaenderungen vorkommen kann, wird vor dem INSERT ein TRUNCATE ausgefuehrt (FME). 
    
    Die Angaben zu den Ebenen sind in task_config:
    
    - ``task_config["vektor_ebenen"]``
    
    Der raeumlichen Indexes kann ebenfalls aufgrund der Locks nicht neu berechnet werden.
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "KopieVek1Ersatz_PG"
        TemplateFunction.__init__(self, task_config, general_config)

        if self.name in self.task_config['ausgefuehrte_funktionen'
                                         ] and self.task_config[
                                                 'task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgefuehrt.")
            self.start()
            self.__execute()

    def __execute(self):
        '''
        Fuehrt den eigentlichen Funktionsablauf aus
        '''
        db = self.general_config['connections']['VEK1_GEODB_PG'].db
        port = self.general_config['connections']['VEK1_GEODB_PG'].port
        host = self.general_config['connections']['VEK1_GEODB_PG'].host
        db_user = self.general_config['connections']['VEK1_GEODB_PG'].username
        schema = db_user
        pw = self.general_config['connections']['VEK1_GEODB_PG'].password
        source_sde = self.task_config['connections']['sde_conn_norm']
        fme_script = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..')
        ) + "\\helpers\\" + "EsriGeodatabase2PostGIS.fmw"

        # Jede Ebene durchgehen
        for ebene in self.task_config['vektor_ebenen']:
            source = ebene['quelle']
            source_table = source.rsplit('\\', 1)[1]
            table = ebene['ziel_vek1'].lower().rsplit('\\', 1)[1]
            ebename = ebene['gpr_ebe'].lower()

            self.logger.info("Ebene " + ebename + " wird nach vek1 kopiert.")
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

            # Pruefen ob es die target Tabelle gibt
            table_sp = table.split('.')
            table_exist_sql = "SELECT 1 FROM information_schema.tables WHERE table_schema = '%s' AND table_name = '%s'" % (table_sp[0], table_sp[1])
            table_exist_results = self.general_config['connections']['VEK1_GEODB_PG'].db_read(table_exist_sql)

            if table_exist_results is None:
                # Gibt es die Ziel-Ebene noch nicht, Abbruch mit Fehlermeldung und Exception
                self.logger.error("Ziel-Ebene " + table + " existiert nicht!")
                raise Exception

            # Eine Liste der Attribute mit Typ Date erstellen (FME braucht diese Info, damit leere Datumsfelder fuer Postgres richtig gesetzt werden koennen)
            datefields = arcpy.ListFields(source, field_type='Date')
            dfield = None
            for datefield in datefields:
                if dfield is None:
                    dfield = datefield.name
                else:
                    dfield = dfield + ' ' + datefield.name

            # Anzahl Records in Source
            count_source = int(arcpy.GetCount_management(source)[0])

            # Daten kopieren
            # Copy-Script, Table Handling auf Truncate umstellen, damit Tabelle nicht gelöscht wird
            self.logger.info(
                    "Ebene %s/%s %s wird geleert (Truncate) und aufgefuellt (Insert)." % (host, db, table)
            )
            # Extra truncate bei 0 Quell-Records, da FME bei 0 Quelldaten kein Truncate macht.
            if count_source == 0:
                truncate_sql = 'TRUNCATE %s' % (table)
                self.general_config['connections']['VEK1_GEODB_PG'].db_write(truncate_sql)

            fme_logfile = iLader.helpers.Helpers.prepare_fme_log(fme_script, (self.task_config['log_file']).rsplit('\\',))

            fme_parameters = {
                    'TABELLEN': source_table,
                    'POSTGIS_DB': db,
                    'POSTGIS_HOST': host,
                    'POSTGIS_PORT': port,
                    'POSTGIS_USER': db_user,
                    'SCHEMA_NAME': schema,
                    'POSTGIS_PASSWORD': pw,
                    'LOGFILE': fme_logfile,
                    'INPUT_SDE': source_sde,
                    'TABLE_HANDLING': "TRUNCATE_EXISTING",
                    'DATEFIELDS': dfield,
                    'TABELLENTYP': tabellentyp
            }
            
            fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=fme_parameters, fme_logfile=fme_logfile, fme_logfile_archive=False)
            fmerunner.run()
            if fmerunner.returncode != 0:
                self.logger.error("FME-Script %s abgebrochen." % (fme_script))
                raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))

            # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
            self.logger.info(
                    "Anzahl Objekte in Quell-Ebene: " + unicode(count_source)
            )
            count_target_sql = 'SELECT COUNT(*) FROM %s' % (table)
            count_target_result = self.general_config['connections']['VEK1_GEODB_PG'].db_read(count_target_sql)
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

            self.logger.info("Ebene " + ebename + " wurde ersetzt")

        self.logger.info("Alle Ebenen wurden ersetzt.")
        self.finish()