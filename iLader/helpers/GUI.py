# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from iLader import __version__
import iLader.helpers.Helpers
from iLader.usecases.Usecase import Usecase
from Tkinter import *
import sys
from iLader.helpers.StdoutToWidget import StdoutToWidget

class iLaderGUI(Frame):
    '''
    
    '''
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        # self.title("iLader v" + __version__)
        self.pack()

        self.chkbox_var = IntVar(self)
        self.chkbox_var.set(0)
        self.optmenu_var = StringVar(self)
        
        
        # Liste mit den offenen Task aus DD auslesen
        self.tasks = iLader.helpers.Helpers.getImportTasks()
        
        self.make_widgets()
        
        
    def make_widgets(self):
        # Überschrift
        self.lbl = Label(self, text="Bitte den gewünschten Import auswählen:")
        self.lbl.pack(side=TOP)
        
        # Auswahlliste mit den Tasks
        self.optmenu = OptionMenu(self, self.optmenu_var, *self.tasks)
        self.optmenu.pack(side=LEFT)
        
        # Checkbox (Task-Config reloaden)
        self.chkbox = Checkbutton(self, text="Reload", variable=self.chkbox_var)
        self.chkbox.pack()
        
        # OK-Knopf
        self.btn_ok = Button(self, text="Import starten", command=self.run_import)
        self.btn_ok.pack(side=BOTTOM)
        
        # Log-Fenster
        self.log_text = Text(self,width=120)
        self.log_text.pack()
#         self.log_text.insert(END, "Hallo Hallo Hallo!!!")
#         self.logger = StdoutToWidget(self.log_text)
#         self.logger.start()
#         sys.stdout = StdoutRedirector(self.log_text)
        
        
    def run_import(self):
        print("sdfsfsdf")
        selected_task = self.optmenu_var.get()
        reload_json = self.chkbox_var.get()
        if selected_task:
            print("Usecase " + selected_task + " ausgewählt.")
            if reload_json == 1:
                reload_json = True
            else:
                reload_json = False
            print("Usecase wird nun ausgeführt...")
            
            #Abmachung: alle Zeichen vor dem ersten Doppelpunkt entsprechen der Task-ID
            task_id = selected_task.split(":")[0]
            uc = Usecase(task_id, reload_json)
            #sys.exit()
        else:
            print("kein Task ausgewählt. Bitte nochmals auswählen.")
            
def main():
    root = Tk()
    root.title("iLader v" + __version__)
    i = iLaderGUI(root)
    l = StdoutToWidget(i.log_text)
    l.start()
    root.mainloop()

if __name__ == "__main__": 
    main()