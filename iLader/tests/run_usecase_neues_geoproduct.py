# -*- coding: utf-8 -*-
from iLader.usecases import NeuesGeoprodukt

uc = NeuesGeoprodukt("23424234", True)
print uc.name
print uc.task_id