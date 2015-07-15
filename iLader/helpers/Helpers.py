# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import os
import configobj
from iLader.helpers import Crypter

def get_general_configfile_from_envvar():
    '''
    Holt den Pfad zur Konfigurationsdatei aus der Umgebungsvariable
    GEODBIMPORTHOME und gibt dann den vollständigen Pfad (inkl. Dateiname)
    der Konfigurationsdatei zurück.
    '''
    config_directory = os.environ['GEODBIMPORTHOME']
    config_filename = "config.ini"
    
    config_file = os.path.join(config_directory, config_filename)
    
    return config_file
    
def decrypt_passwords(section, key):
    '''
    Entschlüsselt sämtliche Passworte in der zentralen
    Konfigurationsdatei. Wird aus der ConfigObj.walk-Funktion
    aus aufgerufen. Deshalb sind section und key als
    Parameter obligatorisch.
    :param section: ConfigObj.Section-Objekt
    :param key: aktueller Schlüssel im ConfigObj-Objekt
    '''
    # Hilfsklasse für die Entschlüsselung
    
    # Annahme: alle Keys, die "password" heissen, enthalten zu entschlüsselnde Passwörter
    crypter = Crypter()
    if key == "password":
        encrypted_password = section[key]
        decrypted_password = crypter.decrypt(encrypted_password)
        # Wert in der Config ersetzen
        section[key] = decrypted_password
    
def init_generalconfig():
    '''
    liest die zentrale Konfigurationsdatei in ein ConfigObj-Objet ein.
    Dieser kann wie ein Dictionary gelesen werden.
    '''
    config_filename = get_general_configfile_from_envvar()
    config_file = configobj.ConfigObj(config_filename, encoding="UTF-8")
    
    # Die Walk-Funktion geht rekursiv durch alle
    # Sections und Untersections der Config und 
    # ruft für jeden Key die angegebene Funktion
    # auf
    config_file.walk(decrypt_passwords)
    
    return config_file  
    
def getImportTasks():
    general_config = init_generalconfig()
    db = general_config['instances']['team']
    user = general_config['users']['geodb_dd']['username']
    pw = general_config['users']['geodb_dd']['password']
    schema = general_config['users']['geodb_dd']['schema']
    sql = "SELECT t.TASK_OBJECTID, u.UC_BEZEICHNUNG, g.GPR_BEZEICHNUNG, z.GZS_JAHR, z.GZS_VERSION FROM " + schema + ".TB_TASK t LEFT JOIN " + schema + ".TB_USECASE u ON t.UC_OBJECTID=u.UC_OBJECTID LEFT JOIN " + schema + ".TB_GEOPRODUKT_ZEITSTAND z ON z.GZS_OBJECTID = t.GZS_OBJECTID LEFT JOIN " + schema + ".TB_GEOPRODUKT g ON z.GPR_OBJECTID = g.GPR_OBJECTID WHERE t.TASK_STATUS=1 ORDER BY g.GPR_BEZEICHNUNG ASC"
    
    dd_connection = cx_Oracle.connect(user, pw, db)
    cursor = dd_connection.cursor()
    cursor.execute(sql)
    task_query_result = cursor.fetchall()
    
    tasks = []
    
    for row in task_query_result:
        task_objectid = str(row[0]).decode('cp1252')
        uc_bezeichnung = str(row[1]).decode('cp1252')
        gpr_bezeichnung = str(row[2]).decode('cp1252')
        gzs_jahr = str(row[3]).decode('cp1252')
        gzs_version = str(row[4]).decode('cp1252')
        #Abmachung: alle Zeichen vor dem ersten Doppelpunkt entsprechen der Task-ID
        parameter_string = task_objectid + ": " + gpr_bezeichnung + " " + gzs_jahr + "_" + gzs_version + " (" + uc_bezeichnung + ")"
        
        tasks.append(parameter_string)
    
    cursor.close()
    dd_connection.close()    
    
    return tasks