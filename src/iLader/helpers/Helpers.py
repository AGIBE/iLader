# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
from iLader.__init__ import __version__  
import os
import csv
import getpass
import datetime

def get_config():
    config = AGILib.Configuration(configfile_envvar='GEODBIMPORTHOME').config
    connection_infos = AGILib.Configuration(configfile_path=config['agilib_connections']).config
    connections = {}
    connection_files = {}
    # Alle benötigten Connections erstellen
    connections['TEAM_GEODB_DD_ORA'] = AGILib.Connection(db=connection_infos['db']['team']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb_dd']['username'], password=connection_infos['user']['geodb_dd']['password'])
    connections['VEK1_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['vek1']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    connections['VEK2_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['vek2']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    connections['VEK3_GEODB_ORA'] = AGILib.Connection(db=connection_infos['db']['vek3']['ora_db'], db_type='oracle', username=connection_infos['user']['geodb']['username'], password=connection_infos['user']['geodb']['password'])
    connections['WORK_GDBP_ORA'] = AGILib.Connection(db=connection_infos['db']['work']['ora_db'], db_type='oracle', username=connection_infos['user']['gdbp']['username'], password=connection_infos['user']['gdbp']['password'])
    connections['WORK_OEREB_PG'] = AGILib.Connection(db=connection_infos['db']['work']['pg_db'], db_type='postgres', username=connection_infos['user']['oereb']['username'], password=connection_infos['user']['oereb']['password'], host=connection_infos['db']['work']['pg_host'], port=connection_infos['db']['work']['pg_port'])

    # Alle benötigten Connection-Files erstellen
    connection_files['VEK1_GEODB_ORA'] = connections['VEK1_GEODB_ORA'].create_sde_connection()
    connection_files['VEK2_GEODB_ORA'] = connections['VEK2_GEODB_ORA'].create_sde_connection()
    connection_files['VEK3_GEODB_ORA'] = connections['VEK3_GEODB_ORA'].create_sde_connection()

    config['connections'] = connections
    config['connection_files'] = connection_files
    config['connection_infos'] = connection_infos
    return config

def register_installations(general_config, logger):
    '''
    Legt die installierte Version inkl. Angabe zu User und PC zentral in csv-Datei ab.
    '''
    try:
        instfile = general_config['INSTALLATION']['instreg']
        usrlist = []
        usr = getpass.getuser()
        pc = os.environ['COMPUTERNAME']
        # csv einlesen
        with open(instfile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=str(u';'))
            for row in spamreader:
                usrlist.append([row[0], row[1], row[2]])
        # csv allenfalls ergaenzen
        if not [__version__, usr, pc] in usrlist:
            with open(instfile, 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=str(u';'))
                spamwriter.writerow([__version__ , usr, pc, datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")])
    except Exception as e:
        logger.warn('Installationsversion konnte nicht zentral abgelegt werden. ' + e)
        pass

    
def get_import_tasks():
    tasks = []

    general_config = get_config()

    import_tasks_sql = "SELECT t.TASK_OBJECTID, u.UC_BEZEICHNUNG, g.GPR_BEZEICHNUNG, z.GZS_JAHR, z.GZS_VERSION FROM TB_TASK t LEFT JOIN TB_USECASE u ON t.UC_OBJECTID=u.UC_OBJECTID LEFT JOIN TB_GEOPRODUKT_ZEITSTAND z ON z.GZS_OBJECTID = t.GZS_OBJECTID LEFT JOIN TB_GEOPRODUKT g ON z.GPR_OBJECTID = g.GPR_OBJECTID WHERE t.TASK_STATUS=1 ORDER BY g.GPR_BEZEICHNUNG ASC"
    import_tasks_result = general_config['connections']['TEAM_GEODB_DD_ORA'].db_read(import_tasks_sql)
    
    for import_task in import_tasks_result:
        parameter_string = "%s: %s %s_%s (%s)" % (unicode(import_task[0]), import_task[2], unicode(import_task[3]), unicode(import_task[4]), import_task[1])
        tasks.append(parameter_string) 
    
    return tasks