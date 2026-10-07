# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory.interfaces import ICategorizedElementsUpdatedEvent
from collective.iconifiedcategory.interfaces import ICategorizedElementUpdatedEvent
from collective.iconifiedcategory.interfaces import IIconifiedAttrChangedEvent
from collective.iconifiedcategory.interfaces import IIconifiedCategoryChangedEvent


try:
    from zope.interface.interfaces import ObjectEvent
except ImportError:
    from zope.component.interfaces import ObjectEvent

from zope.interface import implementer


@implementer(IIconifiedCategoryChangedEvent)
class IconifiedCategoryChangedEvent(ObjectEvent):

    def __init__(self, object, category, sort=False):
        super(IconifiedCategoryChangedEvent, self).__init__(object)
        self.category = category
        self.sort = sort


@implementer(IIconifiedAttrChangedEvent)
class IconifiedAttrChangedEvent(ObjectEvent):

    def __init__(self, object, attr_name, old_values, new_values, is_created=False):
        super(IconifiedAttrChangedEvent, self).__init__(object)
        self.attr_name = attr_name
        self.old_values = old_values
        self.new_values = new_values
        self.is_created = is_created


@implementer(ICategorizedElementsUpdatedEvent)
class CategorizedElementsUpdatedEvent(ObjectEvent):
    """"""


@implementer(ICategorizedElementUpdatedEvent)
class CategorizedElementUpdatedEvent(ObjectEvent):

    def __init__(self, object, parent, old_values, new_values, limited=False):
        super(CategorizedElementUpdatedEvent, self).__init__(object)
        self.object = object
        self.parent = parent
        self.old_values = old_values
        self.new_values = new_values
        self.limited = limited
