# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateFunction import TemplateFunction
from iLader.helpers.Helpers import oereb_copy_transferstruktur
import os
import sys

class TransferVek2_PG(TemplateFunction):
    '''
    Kopiert die ÖREBK-Transferstruktur nach vek2 (PostgreSQL).
    Es werden nur diejenigen Liefereinheiten und Schemas kopiert,
    die zum importierten Geoprodukt gehören. Wenn zu diesem
    Geoprodukt keine ÖREBK-Tickets gefunden werden, wird die
    ÖREBK-Transferstruktur gar nicht kopiert.
    '''

    def __init__(self, task_config, general_config):
        '''
        Constructor
        :param task_config: Vom Usecase initialisierte task_config (Dictionary)
        '''
        self.name = "TransferVek2_PG"
        TemplateFunction.__init__(self, task_config, general_config)
        
        if self.name in self.task_config['ausgefuehrte_funktionen'] and self.task_config['task_config_load_from_JSON']:
            self.logger.info("Funktion " + self.name + " wird ausgelassen.")
        else:
            self.logger.info("Funktion " + self.name + " wird ausgefuehrt.")
            self.start()
            self.__execute()

    def __execute(self):
        '''
        Fuehrt den eigentlichen Funktionsablauf aus
        '''
        self.logger.info("Die ÖREBK-Transferstruktur PostGIS wird von team nach vek2 kopiert.")
        oereb_copy_transferstruktur(self.general_config['connections']['VEK2_OEREB_PG'], self.general_config, self.task_config ,self.logger)

        self.finish()