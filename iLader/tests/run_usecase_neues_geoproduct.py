# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from iLader.usecases import NeuesGeoprodukt

uc = NeuesGeoprodukt("666", False)
print(uc.name)
print(uc.task_id)
print(uc.general_config)