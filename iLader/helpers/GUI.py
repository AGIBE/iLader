# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from iLader import __version__
import iLader.helpers.Helpers
from iLader.usecases.Usecase import Usecase
from Tkinter import *
from iLader.helpers.StdoutToWidget import StdoutToWidget
import tkMessageBox
import ScrolledText

class iLaderGUI(Frame):
    '''
    GUI-Klasse (Tkinter-Frame), die das GUI für die Ausführung
    eines Imports implementiert. Die offenen Import-Tasks werden
    mit der Helper-Funktion get_import_tasks ermittelt.
    '''
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack()

        self.chkbox_var = IntVar(self)
        self.chkbox_var.set(0)
        self.optmenu_var = StringVar(self)
        
        # Liste mit den offenen Task aus DD auslesen
        self.tasks = iLader.helpers.Helpers.get_import_tasks()
        
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

        # Beenden-Knopf        
        self.btn_quit = Button(self, text="Beenden", command=self.quit)
        self.btn_quit.pack(side=BOTTOM)
        
        # Log-Fenster (ScrolledText)
        self.log_text = ScrolledText.ScrolledText(self, width=150)
        self.log_text.pack()

    def quit(self):
        sys.exit()
        
    def run_import(self):
        self.selected_task = self.optmenu_var.get()
        self.reload_json = self.chkbox_var.get()
        if self.selected_task:
            self.btn_ok.configure(state=DISABLED)
            self.btn_quit.configure(state=DISABLED)
            if self.reload_json == 1:
                self.reload_json = True
            else:
                self.reload_json = False
            
            #Abmachung: alle Zeichen vor dem ersten Doppelpunkt entsprechen der Task-ID
            self.task_id = self.selected_task.split(":")[0]
            
            self.uc = Usecase(self.task_id, self.reload_json)
            self.uc.run()
            
            self.btn_ok.configure(state=NORMAL)
            self.btn_quit.configure(state=NORMAL)
            
        else:
            tkMessageBox.showwarning('iLader', 'Es wurde kein Geoprodukt ausgewählt. Bitte erneut versuchen!')
            
def main():
    root = Tk()
    root.title("iLader v" + __version__)
    i = iLaderGUI(root)
    l = StdoutToWidget(i.log_text)
    l.start()
    root.mainloop()

if __name__ == "__main__": 
    main()