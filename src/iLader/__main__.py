# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from iLader import __version__
import iLader.helpers.Helpers
from iLader.usecases.Usecase import Usecase

def run_taskid(args):
    uc = Usecase(args.TASKID, args.resume)
    uc.run()

def list_taskids(args):
    tasks = iLader.helpers.Helpers.get_import_tasks()
    for task in tasks:
        print(task)
        
def main():
    version_text = "iLader v" + __version__
    parser = argparse.ArgumentParser(description="Kommandozeile fuer den iLader. Fuehrt Tasks aus und zeigt offene Tasks an.", prog="iLader.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # LIST-Befehl
    list_parser = subparsers.add_parser('list', help='zeigt alle ausfuehrbaren Tasks an.')
    list_parser.set_defaults(func=list_taskids)
    
    # RUN-Befehl
    run_parser = subparsers.add_parser('run', help='fuehrt den angegebenen Task aus.')
    run_parser.add_argument("TASKID", type=int, help="auszufuehrende Task-ID.")
    run_parser.add_argument("-r", "--resume", help="Setzt den Import an der abgebrochenen Stelle fort.", action="store_true", required=False)
    run_parser.set_defaults(func=run_taskid)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()