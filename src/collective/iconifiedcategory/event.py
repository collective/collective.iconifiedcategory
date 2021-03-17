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
from collective.iconifiedcategory.interfaces import IIconifiedModifiedEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class IconifiedModifiedEvent(ObjectEvent):
    implements(IIconifiedModifiedEvent)


class IconifiedCategoryChangedEvent(ObjectEvent):
    implements(IIconifiedCategoryChangedEvent)

    def __init__(self, object, category, sort=False):
        super(IconifiedCategoryChangedEvent, self).__init__(object)
        self.category = category
        self.sort = sort


class IconifiedAttrChangedEvent(ObjectEvent):
    implements(IIconifiedAttrChangedEvent)

    def __init__(self, object, attr_name, old_values, new_values, is_created=False):
        super(IconifiedAttrChangedEvent, self).__init__(object)
        self.attr_name = attr_name
        self.old_values = old_values
        self.new_values = new_values
        self.is_created = is_created


class CategorizedElementsUpdatedEvent(ObjectEvent):
    implements(ICategorizedElementsUpdatedEvent)
