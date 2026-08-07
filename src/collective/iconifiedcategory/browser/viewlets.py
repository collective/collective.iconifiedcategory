# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_parent
from collective.iconifiedcategory.browser.views import CategorizedElementsMixin
from plone.app.layout.viewlets import common as base


class CategorizedChildViewlet(base.ViewletBase):
    """ """


class CategorizedItemInfoViewlet(CategorizedElementsMixin, base.ViewletBase):
    """Viewlet showing the category status icons on a categorized item's view page."""

    @property
    def element(self):
        """The categorized infos of the current item, or None."""
        elements = getattr(aq_parent(self.context), 'categorized_elements', {})
        return elements.get(self.context.UID())

    def render(self):
        if self.element is None:
            return ''
        return super(CategorizedItemInfoViewlet, self).render()

    def show(self, element, attr_prefix):
        return element['{0}_activated'.format(attr_prefix)]

    def show_download(self, element):
        return False
