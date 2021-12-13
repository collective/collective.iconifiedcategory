# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.content.subcategory import ISubcategory
from collective.iconifiedcategory.event import IconifiedAttrChangedEvent
from collective.iconifiedcategory.interfaces import IIconifiedPrintable
from imio.helpers.cache import invalidate_cachekey_volatile_for
from plone import api
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import Redirect
from zope.component import getAdapter
from zope.event import notify


def categorized_content_created(obj, event):

    if hasattr(obj, 'content_category'):
        # if 'to_print' and 'confidential' are managed manually,
        # we may defer events if relevant value found in the REQUEST
        if obj.REQUEST.get('defer_categorized_content_created_event', False):
            return

        # set default values for to_print, confidential and to_sign/signed
        try:
            category = utils.get_category_object(obj, obj.content_category)
        except KeyError:
            return
        # left False if to_print/confidential/to_sign
        # not enabled on ContentCategoryGroup
        category_group = category.get_category_group(category)

        # only set default value if obj was not created with a to_print=True
        if category_group.to_be_printed_activated and not getattr(obj, 'to_print', False):
            obj.to_print = category.to_print
            # notifying IconifiedAttrChangedEvent for 'to_print' is done in categorized_content_updated
        elif not category_group.to_be_printed_activated:
            obj.to_print = False

        # only set default value if obj was not created with a confidential=True
        if category_group.confidentiality_activated and not getattr(obj, 'confidential', False):
            obj.confidential = category.confidential
            notify(IconifiedAttrChangedEvent(
                obj,
                'confidential',
                old_values={},
                new_values={'confidential': obj.confidential},
                is_created=True
            ))
        elif not category_group.confidentiality_activated:
            obj.confidential = False

        # only set default value if obj was not created with a to_sign=True or signed=True
        if category_group.signed_activated and not (getattr(obj, 'to_sign', False) or getattr(obj, 'signed', False)):
            obj.to_sign = category.to_sign
            obj.signed = category.signed
            notify(IconifiedAttrChangedEvent(
                obj,
                'to_sign',
                old_values={},
                new_values={'to_sign': obj.to_sign,
                            'signed': obj.signed},
                is_created=True
            ))

        elif not category_group.signed_activated:
            obj.to_sign = False
            obj.signed = False

        # only set default value if obj was not created with a publishable=True
        if category_group.publishable_activated and not getattr(obj, 'publishable', False):
            obj.publishable = category.publishable
            notify(IconifiedAttrChangedEvent(
                obj,
                'publishable',
                old_values={},
                new_values={'publishable': obj.publishable},
                is_created=True
            ))
        elif not category_group.publishable_activated:
            obj.publishable = False

        # to_print changed event is managed in categorized_content_updated
        categorized_content_updated(event, is_created=True)

        if utils.is_file_type(obj.portal_type):
            file_field_name = IPrimaryFieldInfo(obj).fieldname
            size = getattr(obj, file_field_name).size
            if utils.warn_filesize(size):
                plone_utils = api.portal.get_tool('plone_utils')
                plone_utils.addPortalMessage(
                    _("The annex that you just added has a large size and "
                      "could be difficult to download by users wanting to "
                      "view it!"), type='warning')


def content_updated(obj, event):
    if hasattr(obj, 'content_category'):
        categorized_content_updated(event)


def categorized_content_updated(event, is_created=False):
    obj = event.object

    if hasattr(obj, 'content_category'):
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

            adapter = getAdapter(obj, IIconifiedPrintable)
            adapter.update_object()
            notify(IconifiedAttrChangedEvent(
                obj,
                'to_print',
                old_values={'to_print': obj.to_print},
                new_values={'to_print': obj.to_print},
                is_created=is_created
            ))
        # we may defer call to utils.update_categorized_elements
        # if relevant value found in the REQUEST
        # this is useful when adding several categorized elements without
        # calling update_categorized_elements between every added element
        if obj.REQUEST.get('defer_update_categorized_elements', False):
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
            limited=False,
            sort=event.sort,
            logging=True
        )


def categorized_content_removed(event):
    if hasattr(event.object, 'content_category'):
        obj = event.object
        utils.remove_categorized_element(obj.aq_parent, obj)


def categorized_content_container_cloned(container, event):
    if container.REQUEST.get('defer_update_categorized_elements', False):
        return
    utils.update_all_categorized_elements(container)


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
    # make sure the 'listing' scale image is created
    category.restrictedTraverse('@@images').scale(scale='listing')
    _cookCssResources()


def container_modified(obj, event):
    """When a category container (so a CategoryGroup or a Category)
       is modified (meaning element added/removed/position changed)
       invalidate date used for utils.get_ordered_categories caching."""
    invalidate_cachekey_volatile_for(
        'collective.iconifiedcategory.utils.get_ordered_categories', get_again=True)
