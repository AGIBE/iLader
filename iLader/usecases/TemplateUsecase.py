'''
Created on 09.01.2015

@author: Peter Schär
'''
import logging
import iLader.helpers

class TemplateUsecase(object):
    '''
    Diese Klasse ist eine abstrakte Klasse, von der
    sämtliche Usecases erben. Als abstrakte Klasse wird
    sie nie selber ausgeführt werden, sie dient nur als
    Vorlage und enthält Code, der von allen Usecases
    geteilt wird.
    '''


    def __init__(self, taskid, override_task):        
        '''
        Constructor
        :param taskid: Eindeutige ID des auszuführenden Tasks, stammt aus TB_IMPORTE_GEODB.taskid
        :param override_task: soll die Task-Konfiguration neu generiert werden (TRUE) oder nicht (FALSE)
        '''
        self.config = self.__init_config()
        self.logger = self.__init_logging()
    
    def __create_loghandler_file(self, filename):
        '''
        Konfiguriert einen File-Loghandler
        :param filename: Name (inkl. Pfad) des Logfiles 
        '''
        
        file_formatter = logging.Formatter('%(asctime)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        
        h = logging.FileHandler(filename)
        h.setLevel(logging.DEBUG)
        h.setFormatter(file_formatter)
        
        return h
    
    def __create_loghandler_arcgis(self):
        '''
        Konfiguriert einen ArcGIS-Loghandler
        Inspiriert durch: http://ideas.arcgis.com/ideaView?id=087E00000004H3yIAE
        '''
        # Das gewünschte Format der Log-Message wird definiert
        arcpy_formatter = logging.Formatter('%(asctime)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        
        h = iLader.helpers.ArcGISLogHandler()
        h.setFormatter(arcpy_formatter)
        h.setLevel(logging.DEBUG)
        
        return h
    
    def __init_logging(self):
        '''
        Der Logger wird mit zwei Handlern (arcpy und file) initialisiert
        '''
        logger = logging.getLogger("iLaderLogger")
        logger.setLevel(logging.DEBUG)
        
        # Diese leere Initialisierung ist notwendig, damit der Logger
        # mehrfach in einer Session aufgerufen werden kann. Ansonsten
        # gibt es einen Fehler
        # inspiriert durch: http://ideas.arcgis.com/ideaView?id=087E00000004H3yIAE
        logger.handlers = []
        
        logger.addHandler(self.__create_loghandler_arcgis())
        logger.addHandler(self.__create_loghandler_file(self.config['log_file']))
        
        return logger
    
    def __init_config(self):
        d = {}
        
        return d