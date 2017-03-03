# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zExceptions import Redirect
from zope.component import getAdapter
from zope.event import notify

from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.content.subcategory import ISubcategory
from collective.iconifiedcategory.event import \
    IconifiedConfidentialChangedEvent
from collective.iconifiedcategory.event import IconifiedPrintChangedEvent
from collective.iconifiedcategory.interfaces import IIconifiedPrintable


def categorized_content_created(event):

    if hasattr(event.object, 'content_category'):
        # if 'to_print' and 'confidential' are managed manually,
        # we may defer events if relevant value found in the REQUEST
        if event.object.REQUEST.get('defer_categorized_content_created_event', False):
            return

        if hasattr(event.object, 'confidential'):
            notify(IconifiedConfidentialChangedEvent(
                event.object,
                None,
                event.object.confidential,
            ))
        categorized_content_updated(event)

        if utils.is_file_type(event.object.portal_type):
            file_field_name = IPrimaryFieldInfo(event.object).fieldname
            size = getattr(event.object, file_field_name).size
            if utils.warn_filesize(size):
                plone_utils = api.portal.get_tool('plone_utils')
                plone_utils.addPortalMessage(
                    _("The annex that you just added has a large size and "
                      "could be difficult to download by users wanting to "
                      "view it!"), type='warning')


def content_updated(event):
    if hasattr(event.object, 'content_category'):
        categorized_content_updated(event)


def categorized_content_updated(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        target = utils.get_category_object(obj, obj.content_category)

        if hasattr(obj, 'to_print'):
            # if current 'to_print' is None, it means that current content
            # could not be printable, but as it changed,
            # in this case we use the default value
            if obj.to_print is None:
                category = utils.get_category_object(obj, obj.content_category)
                category_group = category.get_category_group(category)
                if category_group.to_be_printed_activated:
                    obj.to_print = category.to_print

            adapter = getAdapter(event.object, IIconifiedPrintable)
            adapter.update_object()
            notify(IconifiedPrintChangedEvent(
                obj,
                obj.to_print,
                obj.to_print,
            ))
        # we may defer call to utils.update_categorized_elements
        # if relevant value found in the REQUEST
        # this is useful when adding several categorized elements without
        # calling update_categorized_elements between every added element
        if event.object.REQUEST.get('defer_update_categorized_elements', False):
            return

        utils.update_categorized_elements(obj.aq_parent, obj, target)


def content_category_updated(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        target = utils.get_category_object(obj, obj.content_category)
        utils.update_categorized_elements(
            obj.aq_parent,
            obj,
            target,
            limited=True,
            sort=event.sort,
            logging=True
        )


def categorized_content_removed(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        utils.remove_categorized_element(obj.aq_parent, obj)


def categorized_content_container_cloned(event):
    if event.object.REQUEST.get('defer_update_categorized_elements', False):
        return
    utils.update_all_categorized_elements(event.object)


def category_before_remove(obj, event):
    # do not fail if removing the Plone Site
    if not event.object.meta_type == 'Plone Site' and \
       ICategory.providedBy(obj) is True:
        if utils.has_relations(obj) is True:
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _('This category or one of is subcategory are used by '
                  'another object and cannot be deleted'),
                type='error',
            )
            raise Redirect(obj.REQUEST.get('HTTP_REFERER'))
        _cookCssResources()


def subcategory_before_remove(obj, event):
    # do not fail if removing the Plone Site
    if not event.object.meta_type == 'Plone Site' and \
       ISubcategory.providedBy(obj) is True:
        if utils.has_relations(obj) is True:
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _('This subcategory is used by another object and cannot be '
                  'deleted'),
                type='error',
            )
            raise Redirect(obj.REQUEST.get('HTTP_REFERER'))


def category_moved(obj, event):
    if event.oldParent is None or event.newParent is None:
        return
    if utils.has_relations(obj) is True:
        IStatusMessage(obj.REQUEST).addStatusMessage(
            _('This category or one of is subcategory are used by '
              'another object and cannot be deleted'),
            type='error',
        )
        raise Redirect(obj.REQUEST.get('HTTP_REFERER'))
    _cookCssResources()


def subcategory_moved(obj, event):
    if event.oldParent is None or event.newParent is None:
        return
    if utils.has_relations(obj) is True:
        IStatusMessage(obj.REQUEST).addStatusMessage(
            _('This subcategory is used by another object and cannot be '
              'deleted'),
            type='error',
        )
        raise Redirect(obj.REQUEST.get('HTTP_REFERER'))


def _cookCssResources():
    # recook portal_css because we need
    # iconified-category.css to be compiled again as it is cached
    portal_css = api.portal.get_tool('portal_css')
    portal_css.cookResources()


def category_created(category, event):
    _cookCssResources()
