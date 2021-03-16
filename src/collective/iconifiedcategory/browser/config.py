# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.event import CategorizedElementsUpdatedEvent
from collective.iconifiedcategory.event import IconifiedCategoryChangedEvent
from plone import api
from Products.Five import BrowserView
from zope.event import notify
from zope.i18n import translate


class UpdateCategorizedElementsBase(BrowserView):

    def __init__(self, context, request):
        super(UpdateCategorizedElementsBase, self).__init__(context, request)
        self._notified = []
        self.sort = self.request.get(
            'sort_updated_categorized_elements', False) is True or False

    def _notify(self, brain):
        if brain.UID in self._notified:
            return
        self._notified.append(brain.UID)
        event = IconifiedCategoryChangedEvent(brain.getObject(), self.context, sort=self.sort)
        notify(event)

    def notify_category_updated(self, obj):
        brains = [b for b in utils.get_back_references(obj)]
        if ICategory.providedBy(obj):
            for subcategory in obj.listFolderContents():
                brains.extend(utils.get_back_references(subcategory))
        for b in brains:
            self._notify(b)

    def _finished(self):
        msg = translate('Elements updated!',
                        domain='collective.iconifiedcategory',
                        context=self.request)
        notify(CategorizedElementsUpdatedEvent(self.context))
        api.portal.show_message(msg, request=self.request)
        self.request.RESPONSE.redirect(self.context.absolute_url())


class UpdateCategorizedElementsConfig(UpdateCategorizedElementsBase):

    def index(self):
        brains = api.content.find(
            context=self.context,
            content_type='ContentCategory',
        )
        for b in brains:
            self.notify_category_updated(b.getObject())
        self._finished()


class UpdateCategorizedElementsCategory(UpdateCategorizedElementsBase):

    def index(self):
        self.notify_category_updated(self.context)
        self._finished()
