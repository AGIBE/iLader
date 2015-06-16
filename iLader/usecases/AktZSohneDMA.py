# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from .TemplateUsecase import TemplateUsecase
import iLader.functions

class AktZSohneDMA(TemplateUsecase):
    '''
    Usecase für den Import eines Geoprodukts mit Zeitstand und
    ohne Datenmodelländerung (s. Detailspezifikation)
    '''


    def __init__(self, task_id, task_config_load_from_JSON):
        '''
        Constructor
        :param task_id: Eindeutige ID des auszuführenden Tasks, stammt aus TB_IMPORTE_GEODB.task_id
        :param task_config_load_from_JSON: soll eine existierende Task-Config eingelesen (TRUE) oder neu erzeugt werden (FALSE)
        '''
        self.name = u"AktZSohneDMA"
        TemplateUsecase.__init__(self, task_id, task_config_load_from_JSON)

        self.logger.info(u"Start der Funktionsausführung")

        try:            
            f = iLader.functions.Generierung(self.logger, self.task_config, self.general_config)
            self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
    
            auszufuehrende_funktionen = [
                         iLader.functions.CheckscriptNormierung,
                         iLader.functions.DeltaChecker,
                         iLader.functions.QAFramework,
                         iLader.functions.QSStatus,
                         iLader.functions.QSBenachrichtigung,
                         iLader.functions.Begleitdaten,
                         iLader.functions.Fonts,
                         iLader.functions.Styles,
                         iLader.functions.Zusatzdaten,
                         iLader.functions.KopieVek2Ersatz,
                         iLader.functions.IndicesVek2,
                         iLader.functions.KopieVek3Neu,
                         iLader.functions.IndicesVek3,
                         iLader.functions.KopieRas1Ersatz,
                         iLader.functions.BegleitdatenReplaceSource,
                         iLader.functions.AktuellerZeitstand,
                         iLader.functions.ZeitstandStatus,
                         iLader.functions.ImportStatus,
                         iLader.functions.ImportArchiv
                         ]
            
            for funktion in auszufuehrende_funktionen:
                f = funktion(self.logger, self.task_config)
                self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
        finally: # Die Ausputzer-Funktion muss immer ausgeführt werden.
            f = iLader.functions.Ausputzer(self.logger, self.task_config)
            self.logger.info(u"Usecase "+ self.name + u": Funktion " + f.name + u" wurde ausgeführt")
