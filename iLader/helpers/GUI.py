# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from iLader import __version__
import iLader.helpers.Helpers
from Tkinter import *
import sys

class iLaderGUI(Frame):
    '''
    
    '''
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        # self.title("iLader v" + __version__)
        self.pack()

        self.chkbox_var = StringVar(self)
        self.optmenu_var = StringVar(self)
        
        # Liste mit den offenen Task aus DD auslesen
        self.tasks = iLader.helpers.Helpers.getImportTasks()
        
        self.make_widgets()
        
        
    def make_widgets(self):
        # Überschrift
        lbl = Label(self, text="Bitte den gewünschten Import auswählen:")
        lbl.pack(side=TOP)
        
        # Auswahlliste mit den Tasks
        optmenu = OptionMenu(self, self.optmenu_var, *self.tasks)
        optmenu.pack(side=LEFT)
        
        # Checkbox (Task-Config reloaden)
        chkbox = Checkbutton(self, text="Reload", variable=self.chkbox_var)
        chkbox.pack()
        
        # OK-Knopf
        btn_ok = Button(self, text="Import starten", command=self.run_import)
        btn_ok.pack(side=BOTTOM)
        
    def run_import(self):
        print("sdfsfsdf")
        selected_task = self.optmenu_var.get()
        reload_json = self.chkbox_var.get()
        if selected_task:
            print("Usecase " + selected_task + " ausgewählt.")
            if reload_json == 1:
                "Die Task-Config wird aus einem bestehenden JSON-File eingelesen."
            else:
                "Die Task-Config wird neu generiert."
            print("Usecase wird nun ausgeführt...")
            sys.exit()
        else:
            print("kein Task ausgewählt. Bitte nochmals auswählen.")
            
def main():
    root = Tk()
    root.title("iLader v" + __version__)
    iLaderGUI(root).pack()
    root.mainloop()

if __name__ == "__main__": 
    main()