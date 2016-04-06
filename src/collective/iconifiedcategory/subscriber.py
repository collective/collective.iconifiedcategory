# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.component import getAdapter

from collective.iconifiedcategory.interfaces import IIconifiedPrintable


def print_changed(event):
    adapter = getAdapter(event.object, IIconifiedPrintable)
    adapter.update_object()
