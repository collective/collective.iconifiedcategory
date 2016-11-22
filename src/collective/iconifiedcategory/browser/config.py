# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Products.Five import BrowserView
from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.category import ICategory


class UpdateCategorizedElementsBase(BrowserView):
    _notified = []

    def _notify(self, brain):
        if brain.UID in self._notified:
            return
        self._notified.append(brain.UID)
        event = ObjectModifiedEvent(brain.getObject())
        notify(event)

    def notify_category_updated(self, obj):
        brains = [b for b in utils.get_back_references(obj)]
        if ICategory.providedBy(obj):
            for subcategory in obj.listFolderContents():
                brains.extend(utils.get_back_references(subcategory))
        for b in brains:
            self._notify(b)


class UpdateCategorizedElementsConfig(UpdateCategorizedElementsBase):

    def process(self):
        brains = api.content.find(
            context=self.context,
            content_type='ContentCategory',
        )
        for b in brains:
            self.notify_category_updated(b.getObject())


class UpdateCategorizedElementsCategory(UpdateCategorizedElementsBase):

    def process(self):
        self.notify_category_updated(self.context)
