# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.content import Container
from zope.interface import implements


class ICategoryConfiguration(IFolder):
    """Marker interface of ContentCategoryConfiguration"""


class CategoryConfiguration(Container):
    implements(ICategoryConfiguration)
