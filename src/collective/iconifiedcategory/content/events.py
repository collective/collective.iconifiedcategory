# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from collective.iconifiedcategory import utils


def categorized_content_updated(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        intids = getUtility(IIntIds)
        target = utils.get_category_object(obj, obj.content_category)
        obj.relatedCategory = RelationValue(intids.getId(target))

        utils.update_categorized_elements(obj.aq_parent, obj, target)


def categorized_content_removed(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        utils.remove_categorized_element(obj.aq_parent, obj)
