# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from iLader.usecases import Usecase

uc = Usecase("200159", False)
uc.run()
print(uc.name)
print(uc.task_id)
print(uc.general_config)
