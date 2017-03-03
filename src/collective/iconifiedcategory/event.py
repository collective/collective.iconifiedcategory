# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.component.interfaces import ObjectEvent
from zope.interface import implements

from collective.iconifiedcategory.interfaces import \
    IIconifiedPrintChangedEvent
from collective.iconifiedcategory.interfaces import \
    IIconifiedConfidentialChangedEvent
from collective.iconifiedcategory.interfaces import \
    IIconifiedCategoryChangedEvent
from collective.iconifiedcategory.interfaces import IIconifiedModifiedEvent


class IconifiedChangedEvent(ObjectEvent):

    def __init__(self, object, old_value, new_value):
        super(IconifiedChangedEvent, self).__init__(object)
        self.old_value = old_value
        self.new_value = new_value


class IconifiedModifiedEvent(ObjectEvent):
    implements(IIconifiedModifiedEvent)


class IconifiedCategoryChangedEvent(ObjectEvent):
    implements(IIconifiedCategoryChangedEvent)

    def __init__(self, object, sort=False):
        super(IconifiedCategoryChangedEvent, self).__init__(object)
        self.sort = sort


class IconifiedPrintChangedEvent(IconifiedChangedEvent):
    implements(IIconifiedPrintChangedEvent)


class IconifiedConfidentialChangedEvent(IconifiedChangedEvent):
    implements(IIconifiedConfidentialChangedEvent)
