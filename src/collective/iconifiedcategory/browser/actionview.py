# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Products.Five import BrowserView
from z3c.json.interfaces import IJSONWriter
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent

from collective.iconifiedcategory import utils
from collective.iconifiedcategory.event import IconifiedPrintChangedEvent
from collective.iconifiedcategory.event import IconifiedConfidentialChangedEvent


class BaseView(BrowserView):
    attribute_name = ''

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
            value = self.convert_value(self.request.get('iconified-value'))
            status, msg = self.set_value(value)
            values['status'] = status
            if msg:
                values['msg'] = self._translate(msg)
            notify(ObjectModifiedEvent(self.context))
        except Exception:
            values['status'] = 1
            values['msg'] = self._translate('Error during process')
        return writer.write(values)

    def set_value(self, value):
        setattr(self.context, self.attribute_name, value)

    @staticmethod
    def convert_value(value):
        values = {
            'false': False,
            'true': True,
        }
        return values.get(value, value)


class ToPrintChangeView(BaseView):
    attribute_name = 'to_print'

    def set_value(self, value):
        old_value = getattr(self.context, self.attribute_name)
        super(ToPrintChangeView, self).set_value(self.convert_value(value))
        notify(IconifiedPrintChangedEvent(self.context, old_value, value))
        return 0, utils.print_message(self.context)


class ConfidentialChangeView(BaseView):
    attribute_name = 'confidential'

    def set_value(self, value):
        old_value = getattr(self.context, self.attribute_name)
        super(ConfidentialChangeView, self).set_value(self.convert_value(value))
        notify(IconifiedConfidentialChangedEvent(self.context, old_value, value))
        return 0, utils.confidential_message(self.context)
