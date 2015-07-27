# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from iLader import __version__
import iLader.helpers.Helpers
from Tkinter import *
import sys

def runImport():
    selected_task = optmenu_var.get()
    if selected_task:
        print("Usecase " + selected_task + " ausgewählt.")
        print("Usecase wird nun ausgeführt...")
        sys.exit()
    else:
        print("kein Task ausgewählt. Bitte nochmals auswählen.")

def main():
    root = Tk()
    root.title("iLader v" + __version__)
    
    lbl = Label(root, text="Bitte den gewünschten Import auswählen:")
    lbl.pack(side=TOP)
    
    tasks = iLader.helpers.Helpers.getImportTasks()
    
    optmenu_var = StringVar(root)
    
    optmenu = OptionMenu(root, optmenu_var, *tasks)
    optmenu.pack(side=LEFT)
    
    btn_ok = Button(root, text="Import starten", command=runImport)
    btn_ok.pack(side=BOTTOM)
    
    root.mainloop()

if __name__ == "__main__":
    main()