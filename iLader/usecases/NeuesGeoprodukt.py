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
        
        f = iLader.functions.Generierung(self.logger, self.task_config, self.general_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")

        auszufuehrende_funktionen = [
                     iLader.functions.CheckscriptNormierung,
                     iLader.functions.QAFramework,
                     iLader.functions.QSStatus,
                     iLader.functions.GPOrdner,
                     iLader.functions.Begleitdaten,
                     iLader.functions.Fonts,
                     iLader.functions.Styles,
                     iLader.functions.Zusatzdaten,
                     iLader.functions.KopieVek2Neu,
                     iLader.functions.IndicesVek2,
                     iLader.functions.KopieVek3Neu,
                     iLader.functions.IndicesVek3,
                     iLader.functions.AktuellerZeitstand,
                     iLader.functions.ZeitstandStatus,
                     iLader.functions.ImportStatus,
                     iLader.functions.ImportArchiv
                     ]
        
        for funktion in auszufuehrende_funktionen:
            f = funktion(self.logger, self.task_config)
            self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        self.logger.info(u"Usecase " + self.name + u"abgeschlossen")
