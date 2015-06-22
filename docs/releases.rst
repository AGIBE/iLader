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
* in setup.py die nötigen Metadaten abfüllen (v.a. Requirements)
* in iLader/__init__.py die Version erhöhen
* wheel erzeugen: ``python setup.py bdist_wheel``
* wheel installieren (s. :doc:`installation`)

Dokumentation builden
---------------------
Doku aus dem Quellcode heraus generieren:
 
* ``sphinx-apidoc -E -f -o docs iLader``
* ausführen zuoberst im Repository, Doku landet im Verzeichnis ``docs``
 
HTML-Version generieren

* ``python setup.py develop`` 
* ``make html``
* im ``docs``-Verzeichnis ausführen
 
Gesamte Doku mit setup.py erstellen
 
* ``python setup.py build_sphinx``
 
Infos:
 
* Kompakte Referenz: http://rest-sphinx-memo.readthedocs.org/en/latest/ReST.html