Übersicht über die Applikation
==============================
Der iLader besteht aus Funktionen und Usecases. Funktionen sind modulare Codeblöcke, die in Usecases kombiniert werden können.
Sowohl die Anzahl Usecases als auch die Anzahl Funktionen ist variabel. Z.Zt. sind folgende Usecases implementiert:

- :py:mod:`.NeuesGeoprodukt`
- :py:mod:`.AktZSohneDMA`
- :py:mod:`.AktZSmitDMA`
- :py:mod:`.Korrektur`
- :py:mod:`.AktTagesakt`
- :py:mod:`.AktohneZSOEREB`
- :py:mod:`.AktTagesaktOEREB`


Die Zuordnung von Funktionen zu Usecases ist in folgender Tabelle dokumentiert:

====================================  ===============  ============  ===========  =========  ===========  ==============  ================
Usecase / Funktion                    NeuesGeoprodukt  AktZSohneDMA  AktZSmitDMA  Korrektur  AktTagesakt  AktohneZSOEREB  AktTagesaktOEREB
====================================  ===============  ============  ===========  =========  ===========  ==============  ================
:py:mod:`.Generierung`                      X                 X             X           X          X              X                X
:py:mod:`.ZeitstandAngelegt`                                                            X                                       
:py:mod:`.CheckscriptNormierung`            X                 X             X           X                                                     
:py:mod:`.DeltaChecker`                                       X             X           X          X              X                X            
:py:mod:`.QAFramework`                      X                 X             X           X          X              X                X              
:py:mod:`.QSStatus`                         X                 X             X           X          X              X                X              
:py:mod:`.QSBenachrichtigung`               X                 X             X           X          X              X                X            
:py:mod:`.GPOrdner`                         X                                                                                               
:py:mod:`.Begleitdaten`                     X                 X             X           X                                                      
:py:mod:`.BegleitdatenReplaceSource`        X                 X             X           X
:py:mod:`.Fonts`                            X                 X             X           X                                                      
:py:mod:`.Styles`                           X                 X             X           X                                                    
:py:mod:`.Zusatzdaten`                      X                 X             X           X          X              X                X         
:py:mod:`.KopieVek2Neu`                     X                                                                                               
:py:mod:`.KopieVek2Ersatz`                                    X             X           X          X              X                X       
:py:mod:`.IndicesVek2`                      X                 X             X                                                               
:py:mod:`.KopieVek1Ersatz`                                                              ?          X                               X         
:py:mod:`.KopieVek3Neu`                     X                 X             X                                                               
:py:mod:`.IndicesVek3`                      X                 X             X                                                               
:py:mod:`.KopieVek3Ersatz`                                                              X          X              X                X         
:py:mod:`.TransferVek2`                                                                                           X                X       
:py:mod:`.TransferVek1`                                                                                                            X
:py:mod:`.KopieRas1Neu`                     X                                                                                            
:py:mod:`.KopieRas1Ersatz`                                    X             X           X                                               
:py:mod:`.AktuellerZeitstand`               X                 X             X                                                               
:py:mod:`.ZeitstandStatus`                  X                 X             X           X                                                      
:py:mod:`.ImportStatus`                     X                 X             X           X          X              X                X        
:py:mod:`.FlagStatus`                                                                              X                                       
:py:mod:`.ImportArchiv`                     X                 X             X           X          X              X                X        
====================================  ===============  ============  ===========  =========  ===========  ==============  ================