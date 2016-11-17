# -*- coding: utf-8 -*-
from collective.iconifiedcategory.adapter import CategorizedObjectAdapter


class TestingCategorizedObjectAdapter(CategorizedObjectAdapter):

    def can_view(self):
        return False
