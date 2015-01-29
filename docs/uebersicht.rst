Übersicht über die Applikation
==============================
Der iLader besteht aus Funktionen und Usecases. Funktionen sind modulare Codeblöcke, die in Usecases kombiniert werden können.
Sowohl die Anzahl Usecases als auch die Anzahl Funktionen ist variabel. Z.Zt. sind folgende Usecases implementiert:

- :py:mod:`.NeuesGeoprodukt`

Die Zuordnung von Funktionen zu Usecases ist in folgender Tabelle dokumentiert:

================================  ===============  ============  ===========  =========  ===========  ==============  ================
Usecase / Funktion                NeuesGeoproduct  AktZSohneDMA  AktZSmitDMA  Korrektur  AktTagesakt  AktohneZSOEREB  AktTagesaktOEREB
================================  ===============  ============  ===========  =========  ===========  ==============  ================
:py:mod:`.Generierung`                  X                 X             X           X          X              X                X
:py:mod:`.ZeitstandAngelegt`                                                        X                                       
:py:mod:`.CheckscriptNormierung`        X                 X             X           X                                                     
:py:mod:`.DeltaChecker`                                   X             X           X          X              X                X            
:py:mod:`.QAFramework`                  X                 X             X           X          X              X                X              
:py:mod:`.QSStatus`                     X                 X             X           X          X              X                X              
:py:mod:`.QSBenachrichtigung`                                                                  X             (X)               X            
:py:mod:`.GPOrdner`                     X                                                                                               
:py:mod:`.Begleitdaten`                 X                 X             X           X                                                      
:py:mod:`.Fonts`                        X                                                                                               
:py:mod:`.Styles`                       X                                                                                               
:py:mod:`.Zusatzdaten`                  X                                                                                               
:py:mod:`.KopieVek2Neu`                 X                                                                                               
:py:mod:`.KopieVek2Ersatz`                                                                                                             
:py:mod:`.IndicesVek2`                  X                                                                                               
:py:mod:`.KopieVek1Ersatz`                                                                                                             
:py:mod:`.KopieVek3Neu`                 X                                                                                               
:py:mod:`.IndicesVek3`                  X                                                                                               
:py:mod:`.KopieVek3Ersatz`                                                                                                             
:py:mod:`.TransferVek2`                                                                                                                
:py:mod:`.TransferVek1`                                                                                                                
:py:mod:`.AktuellerZeitstand`           X                                                                                               
:py:mod:`.ZeitstandStatus`              X                                                                                               
:py:mod:`.ImportStatus`                 X                                                                                               
:py:mod:`.FlagStatus`                                                                                                                 
:py:mod:`.ImportArchiv`                 X                                                                                               
================================  ===============  ============  ===========  =========  ===========  ==============  ================