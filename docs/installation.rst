Installationsanleitung
======================

Systemvoraussetzungen
---------------------
- ArcGIS Desktop 10.2.2 (inkl. Python 2.7.5)
- Oracle Client 32bit 11.2.0.x

Requirements
------------
- arcpy (wird durch ArcGIS Desktop bereitgestellt)
- numpy (wird durch ArcGIS Desktop bereitgestellt)
- cx-Oracle (wird durch KWP-Paket bereitgestellt)
- pycrypto
- configobj
- six
- pyasn1
- python-keyczar

Neuinstallation
---------------
#. Installation cx_Oracle (evtl. Teil von ArcGIS-KWP-Paket)
#. Installation pycrypto

   * exe ausführen
   * richtige Python-Installation auswählen

#. Installation pip
  
   * python get-pip.py
   
#. Installation iLader

   * pip install iLader-0.1-py2-none-any.whl
   
#. Konfiguration iLader

   * Umgebungsvariable GEODBIMPORTHOME setzen
   * Umgebungsvariable GEODBIMPORTSECRET setzen
   * Schlüssel kopieren (Files meta und 1) nach GEODBIMPORTSECRET
   * connections-Verzeichnis kopieren nach GEODBIMPORTSECRET
   * Toolbox einbinden (??)

Aktualisierung
--------------
