# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from AccessControl import Unauthorized
from Products.Five import BrowserView
from Products.CMFCore.permissions import ModifyPortalContent
from z3c.json.interfaces import IJSONWriter
from zope.component import getAdapter
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent

from plone import api

from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.event import IconifiedPrintChangedEvent
from collective.iconifiedcategory.event import IconifiedConfidentialChangedEvent
from collective.iconifiedcategory.interfaces import IIconifiedPrintable


class BaseView(BrowserView):
    attribute_mapping = {}

    def _translate(self, msgid):
        return translate(
            msgid,
            domain='collective.iconifiedcategory',
            context=self.request,
        )

    def __call__(self):
        writer = getUtility(IJSONWriter)
        values = {'status': 0, 'msg': 'success'}
        try:
            self.request.response.setHeader('content-type',
                                            'application/json')
            status, msg = self.set_values(self.get_values())
            values['status'] = status
            if msg:
                values['msg'] = self._translate(msg)
            if not status == 1:
                notify(ObjectModifiedEvent(self.context))
        except Exception:
            values['status'] = 1
            values['msg'] = self._translate(_('Error during process'))
        return writer.write(values)

    def get_current_values(self):
        return {k: getattr(self.context, k)
                for k in self.attribute_mapping.keys()}

    def get_values(self):
        return {k: self.request.get(v)
                for k, v in self.attribute_mapping.items()}

    def _may_set_values(self, values):
        return bool(api.user.has_permission(ModifyPortalContent, obj=self.context))

    def set_values(self, values):
        if not self._may_set_values(values):
            raise Unauthorized

        if not values:
            return 1, self._translate(_('No values to set'))

        for key, value in values.items():
            self.set_value(key, value)
        return 0, self._translate(_('Values have been set'))

    def set_value(self, attrname, value):
        setattr(self.context, attrname, value)

    @staticmethod
    def convert_boolean(value):
        values = {
            'false': False,
            'true': True,
        }
        return values.get(value, value)


class ToPrintChangeView(BaseView):
    attribute_mapping = {
        'to_print': 'iconified-value',
    }

    def _may_set_values(self, values):
        res = super(ToPrintChangeView, self)._may_set_values(values)
        if res:
            # is this functionnality enabled?
            category = utils.get_category_object(self.context, self.context.content_category)
            category_group = category.get_category_group()
            res = category_group.to_be_printed_activated
        return res

    def set_values(self, values):
        old_values = self.get_current_values()
        values['to_print'] = self.convert_boolean(values['to_print'])
        super(ToPrintChangeView, self).set_values(values)
        adapter = getAdapter(self.context, IIconifiedPrintable)
        adapter.update_object()
        notify(IconifiedPrintChangedEvent(
            self.context,
            old_values,
            values,
        ))
        return 0, utils.print_message(self.context)


class ConfidentialChangeView(BaseView):
    attribute_mapping = {
        'confidential': 'iconified-value',
    }

    def _may_set_values(self, values):
        res = super(ConfidentialChangeView, self)._may_set_values(values)
        if res:
            # is this functionnality enabled?
            category = utils.get_category_object(self.context, self.context.content_category)
            category_group = category.get_category_group()
            res = category_group.confidentiality_activated
        return res

    def set_values(self, values):
        old_values = self.get_current_values()
        values['confidential'] = self.convert_boolean(values['confidential'])
        super(ConfidentialChangeView, self).set_values(values)
        notify(IconifiedConfidentialChangedEvent(
            self.context,
            old_values,
            values,
        ))
        return 0, utils.confidential_message(self.context)
