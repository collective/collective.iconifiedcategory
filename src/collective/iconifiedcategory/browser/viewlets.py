# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory.browser.views import CategorizedElementsMixin
from plone.app.layout.viewlets import common as base


class CategorizedChildViewlet(base.ViewletBase):
    """ """


class CategorizedItemInfoViewlet(CategorizedElementsMixin, base.ViewletBase):
    """Viewlet showing the category status icons on a categorized item's view page."""

    def __init__(self, context, request, view, manager=None):
        super(CategorizedItemInfoViewlet, self).__init__(context, request, view, manager)
        self.element = self.context.aq_parent.categorized_elements[self.context.UID()]

    def show(self, element, attr_prefix):
        return element['{0}_activated'.format(attr_prefix)]

    def show_download(self, element):
        return False
