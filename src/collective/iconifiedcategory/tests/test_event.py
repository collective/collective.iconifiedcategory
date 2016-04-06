# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

import unittest

from collective.iconifiedcategory import testing
from collective.iconifiedcategory.event import IconifiedChangedEvent


class TestEvent(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def setUp(self):
        from zope.event import subscribers
        self._old_subscribers = subscribers[:]
        subscribers[:] = []

    def tearDown(self):
        from zope.event import subscribers
        subscribers[:] = self._old_subscribers

    def _notify(self, event):
        from zope.event import notify
        notify(event)

    def test_iconifiedchangedevent(self):
        from zope.event import subscribers
        dummy = []
        subscribers.append(dummy.append)
        event = IconifiedChangedEvent(object(), 'old', 'new')
        self._notify(event)
        self.assertEqual(dummy, [event])
