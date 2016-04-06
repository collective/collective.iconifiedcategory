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
from zope.lifecycleevent import ObjectModifiedEvent


class BaseView(BrowserView):
    attribute_name = ''

    def __call__(self):
        writer = getUtility(IJSONWriter)
        values = {'status': 0, 'msg': 'success'}
        try:
            self.request.response.setHeader('content-type',
                                            'application/json')
            setattr(
                self.context,
                self.attribute_name,
                self.request.get('iconified-value'),
            )
            notify(ObjectModifiedEvent(self.context))
        except:
            values['status'] = 1
            values['msg'] = 'error'
        return writer.write(values)


class ToPrintChangeView(BaseView):
    attribute_name = 'to_print'


class ConfidentialChangeView(BaseView):
    attribute_name = 'confidential'
