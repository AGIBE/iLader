'''
Created on 09.01.2015

@author: Peter Schär
'''
import logging
import arcpy

class ArcGISLogHandler(logging.Handler):
    '''
    Die Klasse ArcGISLogHandler implementiert einen logging.Handler.
    Damit können Log-Messages auch in das ArcGIS Geoprocessing-Log
    geschrieben werden. Sie erscheinen dann entweder im Geoprocessing-
    Fenster oder in der Kommandozeile.
    Inspiriert durch: http://ideas.arcgis.com/ideaView?id=087E00000004H3yIAE
    '''

    def __init__(self):
        '''
        Constructor
        '''
        logging.Handler.__init__(self)
        
    def emit(self, record):
        '''
        Die Methode emit muss overridden werden.
        Mit emit schreibt der Handler die Log-Message raus.
        :param record: Die Logging-Message
        '''
        if record.levelno >= logging.ERROR:
            log_method = arcpy.AddError
        elif record.levelno >= logging.WARNING:
            log_method = arcpy.AddWarning
        else:
            log_method = arcpy.AddMessage
            
        log_method(self.format(record))        