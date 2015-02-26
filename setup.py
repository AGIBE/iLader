# -*- coding: utf-8 -*-
# übernommen aus: https://pythonhosted.org/setuptools/setuptools.html#id24
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
      name = "iLader",
      version = "0.1",
      packages = find_packages(),
      package_data={'': ["*.pyt"]},
      # Abhängigkeiten
      install_requires = ["configobj==5.0.6", "cx-Oracle==5.1.3", "numpy==1.7.1", "six==1.9.0", "pyasn1==0.1.7", "pycrypto>=2.6", "python-keyczar==0.715"],
      # PyPI metadata
      author = "Peter Schär, Manuela Uhlmann",
      author_email = "peter.schaer@bve.be.ch, manuela.uhlmann@bve.be.ch",
      description = "Import-Modul Geodatenbank des Kantons Bern",
      url = "http://www.be.ch/geoportal"
)