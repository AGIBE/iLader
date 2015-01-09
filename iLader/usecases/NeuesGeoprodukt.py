# -*- coding: utf-8 -*-
from .TemplateUsecase import TemplateUsecase
import iLader.functions
'''
Created on 09.01.2015

@author: Peter Schär
'''

class NeuesGeoprodukt(TemplateUsecase):
    '''
    Usecase für den Import eines neuen Geoprodukts (s. Detailspezifikation)
    '''


    def __init__(self, task_id, task_config_load_from_JSON):
        '''
        Constructor
        :param task_id: Eindeutige ID des auszuführenden Tasks, stammt aus TB_IMPORTE_GEODB.task_id
        :param task_config_load_from_JSON: soll die Task-Konfiguration neu generiert werden (TRUE) oder nicht (FALSE)
        '''
        self.name = u"NeuesGeoprodukt"
        TemplateUsecase.__init__(self, task_id, task_config_load_from_JSON)
        
        self.logger.info(u"Start der Funktionsausführung")
        
        self.logger.info(u"Funktion Generierung")
        f1 = iLader.functions.Generierung(self.logger, self.task_config)
        
        self.logger.info(u"Funktion CheckscriptNormierung")
        f2 = iLader.functions.CheckscriptNormierung(self.logger, self.task_config)
        
        self.logger.info(u"Funktion DeltaChecker")
        f3 = iLader.functions.DeltaChecker(self.logger, self.task_config)