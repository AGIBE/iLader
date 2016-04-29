Installationsanleitung
======================

Systemvoraussetzungen
---------------------
- ArcGIS Desktop 10.2.2 (inkl. Python 2.7.5)
- Oracle Client 32bit 11.2.0.x

Requirements
------------
- arcpy (wird durch ArcGIS Desktop bereitgestellt; inkl. numpy)
- cx-Oracle (wird durch KWP-Paket bereitgestellt)
- python-keyczar (inkl. pycrypto)
- configobj
- chromalog
- ArcSDE Command Line Tools

Neuinstallation
---------------
#. Installation pycrypto
   * pycrypto-2.6.win32-py2.7.exe ausführen (``K:\Anwend\GeoDB\P3_Applikation\iLader\Installation``)
   * (Vorkompilierte Binaires gibt es auch hier: http://www.voidspace.org.uk/python/modules.shtml#pycrypto; richtige Python-Installation (2.7) auswählen)

#. Installation pip

   * Systemvariable PATH ergänzen um Pfad zum Python-Binary (``C:\Prog\Python27\ArcGIS10.2``)
   * Systemvariable PATH ergänzen um Pfad zum iLader.exe und pip.exe (``C:\Prog\Python27\ArcGIS10.2\Scripts``)
   * ``python get-pip.py`` ausführen (``K:\Anwend\GeoDB\P3_Applikation\iLader\Installation``)
   * Kontrolle: pip list

#. Installation iLader

   * ``pip install iLader-x.x-py2-none-any.whl`` (``K:\Anwend\GeoDB\P3_Applikation\iLader\Installation``)
   * damit werden die übrigen Requirements automatisch mitinstalliert.
   * Kontrolle (der Version): pip list

#. Konfiguration iLader

   * Umgebungsvariable ``GEODBIMPORTHOME`` setzen (``\\geodb.infra.be.ch\freigabe\Anwendungen\iLader``)
   * Umgebungsvariable ``GEODBIMPORTSECRET`` setzen (``P:\iLader``)
   * Schlüssel von ``K:\Anwend\GeoDBAdmin" (Files ``meta`` und ``1``) nach ``GEODBIMPORTSECRET`` kopieren
   * connections-Verzeichnisse von ``K:\Anwend\GeoDBAdmin\iLader\config_master`` kopieren nach ``GEODBIMPORTSECRET`` und umbenennen auf ``connections``
   * Toolbox einbinden (t.b.d.)

#. Konfiguration EWS, BKT, PROD

   * In ``GEODBIMPORTSECRET`` den entsprechenden Unterordner umbenennen auf ``connections``
   * Umgebungsvariable ``GEODBIMPORTHOME`` auf entsprechenden Freigabeshare anpassen

Aktualisierung
--------------

#. iLader deinstallieren (``pip uninstall iLader``)
#. iLader installieren (``pip install iLader-x.x-py2-none-any.whl``)
#. Alternative: ``pip install --upgrade iLader-x.x-py2-none-any.whl``
#. evtl. Änderungen an Config vornehmen (Connection-Files etc.)
