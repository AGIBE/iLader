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


    def __init__(self, task_id, override_task):
        '''
        Constructor
        '''
        self.name = "NeuesGeoprodukt"
        TemplateUsecase.__init__(self, task_id, override_task)
        
        self.logger.info("Start der Funktionsausführung")