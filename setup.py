# -*- coding: utf-8 -*-
# übernommen aus: https://pythonhosted.org/setuptools/setuptools.html#id24
import ez_setup
from iLader import __version__
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
      name = "iLader",
      packages = find_packages(),
      version = __version__,
      # .pyt-Files werden von Python nicht erkannt. Deshalb müssen sie explizit als Package-Inhalt aufgelistet werden.
      package_data={'': ["*.pyt"]},
      # Abhängigkeiten
      install_requires = ["configobj==5.0.6", "cx-Oracle==5.1.3", "python-keyczar==0.715", "chromalog==1.0.4"],
      # PyPI metadata
      author = "Peter Schär, Manuela Uhlmann",
      author_email = "peter.schaer@bve.be.ch, manuela.uhlmann@bve.be.ch",
      description = "Import-Modul Geodatenbank des Kantons Bern",
      url = "http://www.be.ch/geoportal",
      entry_points={
           'console_scripts': [
                'iLader = iLader.helpers.CommandLine:main'
            ],
            'gui_scripts': [
                'iLaderGUI = iLader.helpers.GUI:main'
            ]         
      }
      # TODO: entry_points einfügen (console_script und gui_script)
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
)