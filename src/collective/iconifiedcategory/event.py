# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory.interfaces import ICategorizedElementsUpdatedEvent
from collective.iconifiedcategory.interfaces import IIconifiedAttrChangedEvent
from collective.iconifiedcategory.interfaces import IIconifiedCategoryChangedEvent
try:
    from zope.interface.interfaces import ObjectEvent
except ImportError:
    from zope.component.interfaces import ObjectEvent
from zope.interface import implementer


class IconifiedCategoryChangedEvent(ObjectEvent):
    implementer(IIconifiedCategoryChangedEvent)

    def __init__(self, object, category, sort=False):
        super(IconifiedCategoryChangedEvent, self).__init__(object)
        self.category = category
        self.sort = sort


class IconifiedAttrChangedEvent(ObjectEvent):
    implementer(IIconifiedAttrChangedEvent)

    def __init__(self, object, attr_name, old_values, new_values, is_created=False):
        super(IconifiedAttrChangedEvent, self).__init__(object)
        self.attr_name = attr_name
        self.old_values = old_values
        self.new_values = new_values
        self.is_created = is_created


class CategorizedElementsUpdatedEvent(ObjectEvent):
    implementer(ICategorizedElementsUpdatedEvent)
