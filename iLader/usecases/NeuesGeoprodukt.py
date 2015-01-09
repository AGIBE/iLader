# -*- coding: utf-8 -*-
from .TemplateUsecase import TemplateUsecase
'''
Created on 09.01.2015

@author: Peter Schär
'''

class NeuesGeoprodukt(TemplateUsecase):
    '''
    classdocs
    '''


    def __init__(self, task_id, override_task):
        '''
        Constructor
        '''
        TemplateUsecase.__init__(self, task_id, override_task)
        self.name = "NeuesGeoprodukt"
        
        self.logger.info("Usecase " + self.name + " ist initialisiert")