# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
import os
import tempfile
import psycopg2
import sys
from iLader.helpers import PostgresHelper

class TransferVek1_PG(TemplateFunction):
    '''
    Kopiert die ÖREBK-Transferstruktur nach vek2 (PostgreSQL).
    Es werden nur diejenigen Liefereinheiten und Schemas kopiert,
    die zum importierten Geoprodukt gehören. Wenn zu diesem
    Geoprodukt keine ÖREBK-Tickets gefunden werden, wird die
    ÖREBK-Transferstruktur gar nicht kopiert.
    '''

    def __init__(self, task_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "TransferVek1_PG"
        TemplateFunction.__init__(self, task_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgefuehrt.")
            self.start()
            self.__execute()

    def __append_transferstruktur(self, source_connection_string, target_connection_string, source_sql, full_tablename):
        # https://codereview.stackexchange.com/questions/115863/run-query-and-insert-the-result-to-another-table
        # Inhalte aus WORK mit COPY TO in ein Temp-File schreiben
        copy_to_query = "COPY (%s) TO STDOUT WITH (FORMAT text)" % (source_sql)
        with tempfile.NamedTemporaryFile('w+t') as fp:
            with psycopg2.connect(source_connection_string) as source_connection:
                with source_connection.cursor() as source_cursor:
                    source_cursor.copy_expert(copy_to_query, fp)

            # Alles ins File rausschreiben
            fp.flush()
            # File auf Anfang zurücksetzen
            fp.seek(0)

            with psycopg2.connect(target_connection_string) as target_connection:
                with target_connection.cursor() as target_cursor:
                    target_cursor.copy_from(file=fp, table=full_tablename)

    def __execute(self):
        '''
        Fuehrt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("Die ÖREBK-Transferstruktur PostGIS wird von team nach vek1 kopiert.")
        oereb_pg_tables = self.task_config['oereb']['tabellen_pg']
        oereb_pg_tables_reversed = oereb_pg_tables[::-1]
        liefereinheiten = self.task_config['oereb']['liefereinheiten']
        oereb_pg_schemas = self.task_config['oereb']['schemas']
        
        if liefereinheiten == '()':
            self.logger.info('Für diesen Import konnten keine ÖREBK-Liefereinheiten ermittelt werden.')
            self.logger.info('Die ÖREBK-Transferstruktur wird daher nicht importiert.')
        else:
            pg_username = self.task_config['schema']['oereb']
            pg_pw = self.task_config['users']['oereb']
            pg_target_db = self.task_config['db_vek1_pg']
            pg_source_db = self.task_config['db_team_pg']
            pg_port = self.task_config['port_pg']
            pg_host = self.task_config['instances']['oereb']
            for schema in oereb_pg_schemas:
                self.logger.info("Bearbeite Schema %s..." % (schema))
                for oereb_pg_table in oereb_pg_tables:
                    full_tablename = schema + "." + oereb_pg_table['tablename']
                    where_clause = "%s IN %s" % (oereb_pg_table['filter_field'], liefereinheiten)
                    delete_sql = "DELETE FROM %s WHERE %s" % (full_tablename, where_clause) 
                    self.logger.info("Deleting...")
                    self.logger.info(delete_sql)
                    PostgresHelper.db_sql(self, pg_host, pg_target_db, pg_username, pg_port, pg_pw, delete_sql, fetch=False, fetchall=False)

                # Beim Einfügen muss die umgekehrte Tabellen-Reihenfolge als beim Löschen verwendet werden
                # Grund: Foreign Key-Constraints
                self.logger.info("Appending...")
                for oereb_pg_table in oereb_pg_tables_reversed:
                    full_tablename = schema + "." + oereb_pg_table['tablename']
                    where_clause = "%s IN %s" % (oereb_pg_table['filter_field'], liefereinheiten)
                    source_sql = "SELECT * FROM %s WHERE %s" % (full_tablename, where_clause)
                    self.logger.info(source_sql)
                    source_connection_string = "user=%s password=%s dbname=%s host=%s port=%s" % (pg_username, pg_pw, pg_source_db, pg_host, pg_port)
                    target_connection_string = "user=%s password=%s dbname=%s host=%s port=%s" % (pg_username, pg_pw, pg_target_db, pg_host, pg_port)
                    self.__append_transferstruktur(source_connection_string, target_connection_string, source_sql, full_tablename)
                    # QS (Objekte zählen)
                    self.logger.info("Counting..")
                    source_count = len(PostgresHelper.db_sql(self, pg_host, pg_source_db, pg_username, pg_port, pg_pw, source_sql, fetch=True, fetchall=True))
                    target_count = len(PostgresHelper.db_sql(self, pg_host, pg_target_db, pg_username, pg_port, pg_pw, source_sql, fetch=True, fetchall=True))
                    self.logger.info("Anzahl Features im Quell-Layer: " + unicode(source_count))
                    self.logger.info("Anzahl Features im Ziel-Layer: " + unicode(target_count))
                    if source_count!=target_count:
                        self.logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
                        self.logger.error("Release wird abgebrochen!")
                        sys.exit()
                    
                    self.logger.info("Die Tabelle %s wurde kopiert." % (full_tablename))
                self.logger.info("Das Schema %s wurde kopiert." % (schema))
                        
            self.logger.info("Die ÖREBK-Transferstruktur PostGIS wurde von team nach vek1 kopiert.")
            self.finish()