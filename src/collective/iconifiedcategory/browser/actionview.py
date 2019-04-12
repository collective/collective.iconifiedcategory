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
from collective.iconifiedcategory.event import IconifiedConfidentialChangedEvent
from collective.iconifiedcategory.event import IconifiedPrintChangedEvent
from collective.iconifiedcategory.event import IconifiedSignedChangedEvent
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
        """Do the work :
           - status :
               -1 --> deactivate;
               0 --> set to False;
               1 --> set to True;
               2 --> error;
           """
        writer = getUtility(IJSONWriter)
        values = {'msg': 'success'}
        try:
            self.request.response.setHeader('content-type',
                                            'application/json')
            status, msg = self.set_values(self.get_values())
            values['status'] = status
            if msg:
                values['msg'] = self._translate(msg)
        except Exception:
            values['status'] = 2
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
            return 2, self._translate(_('No values to set'))

        for key, value in values.items():
            self.set_value(key, value)
        status, msg = self._get_status(values), _('Values have been set')
        if not status == 2:
            notify(ObjectModifiedEvent(self.context))
        return status, msg

    def _get_status(self, values):
        value = values.get(self.attribute_mapping.keys()[0], None)
        if value is False:
            return 0
        elif value is True:
            return 1
        else:
            return -1

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
        return self._get_status(values), utils.print_message(self.context)


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
        return self._get_status(values), utils.confidential_message(self.context)


class SignedChangeView(BaseView):
    attribute_mapping = {
        'signed': 'iconified-value',
        'to_sign': 'iconified-value',
    }

    def _may_set_values(self, values):
        res = super(SignedChangeView, self)._may_set_values(values)
        if res:
            # is this functionnality enabled?
            category = utils.get_category_object(self.context, self.context.content_category)
            category_group = category.get_category_group()
            res = category_group.signed_activated
        return res

    def _get_next_values(self, old_values):
        """ """
        values = {}
        if old_values['to_sign'] is False:
            values['to_sign'] = True
            values['signed'] = False
            status = 0
        elif old_values['to_sign'] is True and old_values['signed'] is False:
            values['to_sign'] = True
            values['signed'] = True
            status = 1
        else:
            # old_values['to_sign'] is True and old_values['signed'] is True
            # disable to_sign and signed
            values['to_sign'] = False
            values['signed'] = False
            status = -1
        return status, values

    def set_values(self, values):
        """Value are setting 'to_print' and 'signed' attributes with following
           possibility depending on allowed ones :
           - False/False;
           - True/False;
           - True/True."""
        old_values = self.get_current_values()
        status, values = self._get_next_values(old_values)
        super(SignedChangeView, self).set_values(values)
        notify(IconifiedSignedChangedEvent(
            self.context,
            old_values,
            values,
        ))
        return status, utils.signed_message(self.context)
