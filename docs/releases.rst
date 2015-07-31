Releases und Builds
===================
Benennung
---------
* Entwicklung von v1 findet im MASTER-Branch statt
* Freigegebene Releases (z.B. zum Testen oder Verteilen) werden mit einem Git-Tag markiert.
* Tags müssen separat gepusht werden.
* Nomenklatur: Start mit 0.1 dann 0.2, 0.3 etc. Die fertige Version ist 1.0

Release builden
---------------
* in setup.py die nötigen Metadaten abfüllen (v.a. wenn sich an den Requirements etwas geändert hat)
* in iLader/__init__.py die Version erhöhen
* Commit und Push
* Create Tag und Push Tag
* wheel erzeugen: ``python setup.py bdist_wheel``  (im root-Verzeichnis ausführen)
* neues wheel liegt im Unterverzeichnis ``dist``
* wheel installieren (s. :doc:`installation`)

Dokumentation builden
---------------------
Doku aus dem Quellcode heraus generieren:
 
* ``sphinx-apidoc -E -f -o docs iLader``  (im root-Verzeichnis ausführen)
* Doku landet im Verzeichnis ``docs``
* Dieser Schritt muss dann gemacht werden, wenn sich an der Struktur des Programmcodes etwas geändert hat (neue Klassen, Klassen umbenannt oder gelöscht).
 
HTML-Version generieren

* ``python setup.py develop`` (im root-Verzeichnis ausführen) 
* ``make html`` (im Unterverzeichnis ``docs`` ausführen)
* Das Ergebnis liegt im Unterverzeichnis ``docs/_build/html/index.html``. 
 
Gesamte Doku mit setup.py erstellen
 
* ``python setup.py build_sphinx`` (im root-Verzeichnis ausführen)
* Das Ergebnis liegt im Unterverzeichnis ``build/sphinx/html/index.html``.
 
Infos:
 
* Kompakte Referenz: http://rest-sphinx-memo.readthedocs.org/en/latest/ReST.html