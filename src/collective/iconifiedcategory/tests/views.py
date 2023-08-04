# -*- coding: utf-8 -*-
from collective.iconifiedcategory.browser.views import CategorizedChildInfosView


class TestingCategorizedChildInfosView(CategorizedChildInfosView):

    def _show_protected_download(self, element):
        """ """
        return False
