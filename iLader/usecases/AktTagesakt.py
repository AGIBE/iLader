# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateUsecase import TemplateUsecase
import iLader.functions

class AktTagesakt(TemplateUsecase):
    '''
    Usecase für die Korrektur eines Geoprodukt-Zeitstands (s. Detailspezifikation)
    '''


    def __init__(self, task_id, task_config_load_from_JSON):
        '''
        Constructor
        :param task_id: Eindeutige ID des auszuführenden Tasks, stammt aus TB_IMPORTE_GEODB.task_id
        :param task_config_load_from_JSON: soll eine existierende Task-Config eingelesen (TRUE) oder neu erzeugt werden (FALSE)
        '''
        self.name = u"AktTagesakt"
        TemplateUsecase.__init__(self, task_id, task_config_load_from_JSON)

        self.logger.info(u"Start der Funktionsausführung")

        try:            
            f = iLader.functions.Generierung(self.logger, self.task_config, self.general_config)
            self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
    
            auszufuehrende_funktionen = [
                         iLader.functions.DeltaChecker,
                         iLader.functions.QAFramework,
                         iLader.functions.QSStatus,
                         iLader.functions.QSBenachrichtigung,
                         iLader.functions.Zusatzdaten,
                         iLader.functions.KopieVek2Ersatz,
                         iLader.functions.KopieVek1Ersatz,
                         iLader.functions.KopieVek3Ersatz,
                         iLader.functions.ImportStatus,
                         iLader.functions.FlagStatus,
                         iLader.functions.ImportArchiv
                         ]
            
            for funktion in auszufuehrende_funktionen:
                f = funktion(self.logger, self.task_config)
                self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        finally: # Die Ausputzer-Funktion muss immer ausgeführt werden.
            f = iLader.functions.Ausputzer(self.logger, self.task_config)
            self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
