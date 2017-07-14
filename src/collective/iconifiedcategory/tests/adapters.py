# -*- coding: utf-8 -*-
from collective.iconifiedcategory.adapter import CategorizedObjectAdapter


class TestingCategorizedObjectAdapter(CategorizedObjectAdapter):

    def can_view(self):
        """Return False if element is confidential."""
        obj = self.brain._unrestrictedGetObject()
        if obj.confidential:
            return False
        else:
            return True
