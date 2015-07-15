# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from iLader import __version__
import iLader.helpers.Helpers
from iLader.usecases.Usecase import Usecase

def main():
    parser = argparse.ArgumentParser(description="Kommandozeile fuer den iLader. Fuehrt Tasks aus und zeigt offene Tasks an.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--show_tasks", help="zeigt alle ausfuehrbaren Tasks an", action="store_true")
    group.add_argument("-r", "--run_task", type=int, help="fuehrt den angegebenen Task aus", metavar="TASK-ID")
    #TODO: Die Option für load_task_config einbauen. Wird nur bei run_task verwendet. Default ist False
    group.add_argument("-v", "--version", help="zeigt die Programmversion an", action="store_true")
    #TODO: Argument für encrypt_pw einfügen
    #TODO: Argument für decrypt_pw einfügen
    args = parser.parse_args()
    
    if args.version:
        print("iLader v" + __version__)
        
    if args.show_tasks:
        tasks = iLader.helpers.Helpers.getImportTasks()
        for task in tasks:
            print(task)
            
    if args.run_task:
        #Abmachung: alle Zeichen vor dem ersten Doppelpunkt entsprechen der Task-ID
        task_id = args.run_task
        load_task_config = False
        uc = Usecase(task_id, load_task_config)

    
if __name__ == "__main__":
    main()