# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime
import fmeobjects

def prepare_fme_log(fme_script, log_directory):
    prefix = os.path.splitext(os.path.basename(fme_script))[0]
    fme_logfilename = prefix + "_fme" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
    fme_logfile = os.path.join(log_directory, fme_logfilename)
    
    return fme_logfile

def fme_runner(fme_script, parameters):
    runner = fmeobjects.FMEWorkspaceRunner()
    # FME-Skript starten
    try:
        # Das FME-Skript führt vor dem Erstellen der Tabelle ein DROP aus
        runner.runWithParameters(str(fme_script), parameters)
        pass
    except fmeobjects.FMEException as ex:
        self.logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        self.logger.error(ex)
        self.logger.error("Import wird abgebrochen!")
        sys.exit()