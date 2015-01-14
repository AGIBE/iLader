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
        
        f = iLader.functions.CheckscriptNormierung(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.QAFramework(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.QSStatus(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.GPOrdner(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.Begleitdaten(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.Fonts(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.Styles(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.Zusatzdaten(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.KopieVek2Neu(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.IndicesVek2(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.KopieVek3Neu(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.IndicesVek3(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.AktuellerZeitstand(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.ZeitstandStatus(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.ImportStatus(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        f = iLader.functions.ImportArchiv(self.logger, self.task_config)
        self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        
        self.logger.info(u"Usecase " + self.name + u"abgeschlossen")
