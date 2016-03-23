# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Products.statusmessages.interfaces import IStatusMessage
from z3c.relationfield import RelationValue
from z3c.relationfield.event import _setRelation
from zExceptions import Redirect
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog

from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.content.subcategory import ISubcategory


def categorized_content_updated(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        intids = getUtility(IIntIds)
        target = utils.get_category_object(obj, obj.content_category)
        relation = RelationValue(intids.getId(target))

        utils.update_categorized_elements(obj.aq_parent, obj, target)
        obj.related_category = relation
        _setRelation(obj, 'related_category', relation)


def categorized_content_removed(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        utils.remove_categorized_element(obj.aq_parent, obj)

        catalog = getUtility(ICatalog)
        catalog.unindex(obj.related_category)


def category_before_remove(obj, event):
    if ICategory.providedBy(obj) is True:
        if utils.has_relations(obj) is True:
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _('This category or one of is subcategory are used by '
                  'another object and cannot be deleted'),
                type='error',
            )
            raise Redirect(obj.absolute_url())


def subcategory_before_remove(obj, event):
    if ISubcategory.providedBy(obj) is True:
        if utils.has_relations(obj) is True:
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _('This subcategory is used by another object and cannot be '
                  'deleted'),
                type='error',
            )
            raise Redirect(obj.absolute_url())
