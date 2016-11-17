Übersicht über die Applikation
==============================
Der iLader besteht aus Funktionen und Usecases. Funktionen sind modulare Codeblöcke, die in Usecases kombiniert werden können.
Sowohl die Anzahl Usecases als auch die Anzahl Funktionen ist variabel.

Usecases
--------
Die Usecases sind in der Tabelle TB_USECASE definiert. Z.Zt. sind folgende Usecases implementiert:

#. Neues Geoprodukt
#. Aktualisierung mit ZS mit DMÄ
#. Aktualisierung mit ZS ohne DMÄ
#. Korrektur Geoproduktzeitstand
#. Aktualisierung tagesaktuelles Geoprodukt
#. Aktualisierung OEREB-Geoprodukt ohne Zeitstand
#. Aktualisierung tagesaktuelles OEREB-Geoprodukt

Funktionen
----------
Die Funktionen sind einerseits in der Tabelle TB_FUNCTION definiert und andererseits ist jede Funktion eine Klasse vom Typ :py:mod:`.TemplateFunction`. Es sind folgende Funktionen implementiert:

#. :doc:`generierung`
#. :py:mod:`.ZeitstandAngelegt`                                       
#. :py:mod:`.CheckscriptNormierung`                                                     
#. :py:mod:`.DeltaChecker`            
#. :py:mod:`.QAFramework`              
#. :py:mod:`.QSStatus`              
#. :py:mod:`.QSBenachrichtigung`            
#. :py:mod:`.GPOrdner`                                                                                               
#. :py:mod:`.Begleitdaten`                                                      
#. :py:mod:`.BegleitdatenReplaceSource`
#. :py:mod:`.Fonts`                                                      
#. :py:mod:`.Styles`                                                    
#. :py:mod:`.Zusatzdaten`         
#. :py:mod:`.KopieVek2Neu`                                                                                               
#. :py:mod:`.KopieVek2Ersatz`       
#. :py:mod:`.IndicesVek2`                                                               
#. :py:mod:`.KopieVek1Ersatz`         
#. :py:mod:`.KopieVek3Neu`                                                               
#. :py:mod:`.IndicesVek3`                                                               
#. :py:mod:`.KopieVek3Ersatz`         
#. :py:mod:`.TransferVek2`
#. :py:mod:`.Transfer2Vek2`
#. :py:mod:`.TransferVek1`
#. :py:mod:`.Transfer2Vek1`
#. :py:mod:`.KopieRas1Neu`                                                                                            
#. :py:mod:`.KopieRas1Ersatz`                                               
#. :py:mod:`.AktuellerZeitstand`                                                               
#. :py:mod:`.ZeitstandStatus`                                               
#. :py:mod:`.GeoDBProzess`                                                                                                       
#. :py:mod:`.ImportStatus`        
#. :py:mod:`.FlagStatus`                                       
#. :py:mod:`.ImportArchiv`
#. :doc:`ausputzer`

Die Zuordnung der Funktionen zu den Usecases wird in der Tabelle TB_USECASE_FUNCTION gemacht. Der View VW_USECASE_FUNCTION stellt die Zuordnung besser lesbar dar. Die Zuordnung kann somit im laufenden Betrieb verändert werden, ohne dass die Software neu verteilt werden muss.
Die Funktionen Generierung und Ausputzer sind spezielle Funktionen. Sie werden nicht in den Tabellen TB_FUNCTION aufgeführt und auch keinem Usecase explizit zugeordnet, weil sie in jedem Fall ausgeführt werden. 
