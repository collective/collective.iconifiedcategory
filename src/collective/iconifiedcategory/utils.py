# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collections import OrderedDict
from collective.iconifiedcategory import CAT_SEPARATOR
from collective.iconifiedcategory import CSS_SEPARATOR
from collective.iconifiedcategory import logger
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.content.categorygroup import ICategoryGroup
from collective.iconifiedcategory.content.subcategory import ISubcategory
from collective.iconifiedcategory.interfaces import IIconifiedCategoryConfig
from collective.iconifiedcategory.interfaces import IIconifiedCategoryGroup
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.interfaces import IIconifiedInfos
from natsort import natsorted
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.memoize import ram
from Products.CMFPlone.utils import safe_unicode
from time import time
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate

import copy
import types


def format_id_css(id):
    return id.replace(CAT_SEPARATOR, CSS_SEPARATOR)


def query_config_root(context):
    """Try to get the categories config root for the given context"""
    adapter = queryAdapter(context, IIconifiedCategoryConfig)
    config_root = adapter and adapter.get_config() or None
    if not config_root and context is not None:
        catalog = api.portal.get_tool('portal_catalog')
        query = {
            'portal_type': 'ContentCategoryConfiguration',
        }
        result = catalog.unrestrictedSearchResults(query)
        if not result:
            return
        config_root = result[0]._unrestrictedGetObject()
    return config_root


def has_config_root(context):
    """Verify if there is a config root for the given context"""
    return query_config_root(context) is not None


def get_config_root(context):
    """Return the categories config root for the given context"""
    config_root = query_config_root(context)
    if not config_root:
        raise ValueError('Categories config cannot be found')
    return get_group(config_root, context)


def get_group(config, context):
    """Return the associated groups for the given context"""
    adapter = getMultiAdapter((config, context), IIconifiedCategoryGroup)
    return adapter.get_group()


def get_categories(context,
                   the_objects=False,
                   only_enabled=True,
                   sort_on='getObjPositionInParent'):
    """Return the categories brains for a specific context"""
    config_root = get_config_root(context)
    config_group = get_group(config_root, context)
    catalog = api.portal.get_tool('portal_catalog')
    query = {
        'object_provides': 'collective.iconifiedcategory.content.category.ICategory',
        'sort_on': sort_on,
        'path': '/'.join(config_group.getPhysicalPath()),
    }
    if only_enabled:
        query['enabled'] = True
    res = catalog.unrestrictedSearchResults(query)
    if the_objects:
        res = [brain.getObject() for brain in res]
    return res


def calculate_category_id(category):
    """Return the caculated category id for a category object"""
    if ICategory.providedBy(category):
        return '{0}-{1}_-_{2}_-_{3}'.format(
            category.aq_parent.aq_parent.aq_parent.id,
            category.aq_parent.aq_parent.id,
            category.aq_parent.id,
            category.id,
        )
    if ISubcategory.providedBy(category):
        return '{0}-{1}_-_{2}_-_{3}_-_{4}'.format(
            category.aq_parent.aq_parent.aq_parent.aq_parent.id,
            category.aq_parent.aq_parent.aq_parent.id,
            category.aq_parent.aq_parent.id,
            category.aq_parent.id,
            category.id,
        )


def get_category_object(context, category_id):
    config_root = get_config_root(context)
    config_group = get_group(config_root, context)
    depth = 1
    if ICategoryGroup.providedBy(config_group):
        depth = 2
    category = config_group
    for path in category_id.split(CAT_SEPARATOR)[depth:]:
        category = category[path]
    if not ICategory.providedBy(category) and not ISubcategory.providedBy(category):
        raise KeyError
    return category


def get_category_icon_url(category):
    portal_url = api.portal.get_tool('portal_url')
    if ICategory.providedBy(category):
        obj = category
    else:
        obj = category.aq_parent

    scale = obj.restrictedTraverse("@@images").scale(scale='listing')

    return u'{0}/@@images/{1}'.format(
        portal_url.getRelativeContentURL(obj),
        scale.__name__)


def update_categorized_elements(parent,
                                obj,
                                category,
                                limited=False,
                                sort=True,
                                logging=False):
    """ Update categorized elements
    parameters:
        - parent : The object parent
        - obj : The categorized element
        - category : The category object
        - limited : Update only category related informations
        - logging : Enables logging
    """
    if 'categorized_elements' not in parent.__dict__:
        parent.categorized_elements = OrderedDict()
    uid, new_infos = get_categorized_infos(obj, category, limited=limited)
    infos = parent.categorized_elements.get(uid, {})
    infos.update(new_infos)
    parent.categorized_elements[uid] = infos
    parent._p_changed = True
    if sort:
        sort_categorized_elements(parent)
    if logging:
        logger.info('Updated categorized elements of {0}'.format(
            obj.absolute_url_path()))


def update_all_categorized_elements(container, limited=False, sort=True):
    # recompute everything if limited=False
    if not limited:
        container.categorized_elements = OrderedDict()
    for obj in container.objectValues():
        if hasattr(obj, 'content_category'):
            try:
                category = get_category_object(obj, obj.content_category)
            except KeyError:
                continue
            uid, new_infos = get_categorized_infos(
                obj,
                category,
                limited=limited,
            )
            infos = container.categorized_elements.get(uid, {})
            infos.update(new_infos)
            container.categorized_elements[uid] = infos
    if container.categorized_elements and sort:
        sort_categorized_elements(container)


def get_ordered_categories_cachekey(method, context, only_enabled=True):
    """ """
    return str(context.REQUEST._debug), get_config_root(context), only_enabled


@ram.cache(get_ordered_categories_cachekey)
def get_ordered_categories(context, only_enabled=True):
    """Return an ordered dict for categories (id and uids)"""
    elements = {}
    config_root = get_config_root(context)
    adapter = getMultiAdapter((config_root, context), IIconifiedCategoryGroup)
    categories = adapter.get_every_categories(only_enabled=only_enabled)
    query = {}
    query['object_provides'] = 'collective.iconifiedcategory.content.subcategory.ISubcategory'
    if only_enabled:
        query['enabled'] = True
    for idx, category in enumerate(categories):
        elements[category.UID] = idx
        elements[calculate_category_id(category.getObject())] = idx
        subcategories = api.content.find(context=category, **query)
        for subcategory in subcategories:
            elements[subcategory.UID] = idx
            elements[calculate_category_id(subcategory.getObject())] = idx
    return elements


def sort_categorized_elements(context):
    """Sort the categorized elements on an object"""
    ordered_categories = get_ordered_categories(context, only_enabled=False)
    # use realsorted on a lowered title so it mixes uppercase and lowercase titles
    try:
        elements = natsorted(
            context.categorized_elements.items(),
            key=lambda x: (ordered_categories[x[1]['category_uid']],
                           safe_unicode(x[1]['title'].lower()),),
        )
    except KeyError:
        return
    context.categorized_elements = OrderedDict([(k, v) for k, v in elements])
    context._p_changed = True


def remove_categorized_element(parent, obj):
    if obj.UID() in getattr(parent, 'categorized_elements', OrderedDict()):
        del parent.categorized_elements[obj.UID()]


def get_categorized_infos(obj, category, limited=False):
    adapter = getAdapter(obj, IIconifiedInfos)
    return obj.UID(), adapter.get_infos(category, limited=limited)


def _categorized_elements(context):
    """Return a deepcopy of the categorized elements of the given context"""
    return copy.deepcopy(
        getattr(context, 'categorized_elements', OrderedDict())
    )


def get_categorized_elements(context,
                             result_type='dict',
                             portal_type=None,
                             sort_on=None,
                             uids=[]):
    """Return categorized elements.
       p_result_type may be :
       - 'dict': default, essential metadata are returned as a dict;
       - 'objects': categorized objects are returned;
       - 'brains': categorized brains are returned."""
    elements = []
    categorized_elements = _categorized_elements(context)
    if not categorized_elements:
        return elements

    uids = uids or categorized_elements.keys()
    query = {'UID': uids}
    # sort in the catalog query if we want brains
    if sort_on and result_type == 'brains':
        query['sort_on'] = sort_on
    if portal_type:
        query['portal_type'] = portal_type
    order = categorized_elements.keys()
    for brain in api.content.find(context=context, **query):
        obj = brain._unrestrictedGetObject()
        adapter = getMultiAdapter(
            (obj.aq_parent, obj.REQUEST, brain),
            IIconifiedContent)
        if adapter.can_view():
            if result_type == 'objects':
                elements.append(brain._unrestrictedGetObject())
            elif result_type == 'brains':
                elements.append(brain)
            else:
                # add 'UID' to the available infos
                tmp = categorized_elements[brain.UID].copy()
                tmp['UID'] = brain.UID
                elements.append(tmp)
    if not sort_on:
        elements = sorted(
            elements,
            key=lambda x: order.index(get_UID(x)),
        )

    if sort_on and not result_type == 'brains':
        if result_type == 'dict':
            elements = sorted(elements, key=lambda x, sort_on=sort_on: x[sort_on])
        else:
            elements = sorted(elements, key=lambda x, sort_on=sort_on: getattr(x, sort_on))
    return elements


def get_UID(obj):
    uid = getattr(obj, 'UID', None) or obj['UID']
    if isinstance(uid, types.MethodType):
        uid = uid()
    return uid


def get_back_references(obj):
    portal = api.portal.get()
    return api.content.find(context=portal, content_category_uid=obj.UID())


def has_relations(obj):
    for relation in get_back_references(obj):
        return True
    if ICategory.providedBy(obj):
        for subcategory in obj.listFolderContents():
            for relation in get_back_references(subcategory):
                return True
    return False


def calculate_filesize(size):
    unit = 'B'
    factor = 1
    sizes = {
        1024. * 1024 * 1024 * 1024: 'TB',
        1024. * 1024 * 1024: 'GB',
        1024. * 1024: 'MB',
        1024.: 'KB',
    }
    for s, u in sizes.items():
        if size >= s:
            unit = u
            factor = s
            break
    size = round(size / factor, 1)
    if unit in ('B', 'KB'):
        size = int(size)
    return '{0} {1}'.format(size, unit)


def warn_filesize(size):
    filesizelimit = api.portal.get_registry_record(
        'filesizelimit',
        interface=IIconifiedCategorySettings,
    )
    if size > filesizelimit:
        return True
    return False


def render_filesize(size):
    pretty_filesize = calculate_filesize(size)
    if warn_filesize(size):
        pretty_filesize = \
            u"<span class='warn_filesize' title='{0}'>{1}</span>".format(
                translate('help_warn_filesize',
                          domain='collective.iconifiedcategory',
                          context=getRequest(),
                          default='Annex size is huge, it could '
                          'be difficult to be downloaded!'),
                pretty_filesize)
    return pretty_filesize


def print_message(obj=None, to_print_value=None):
    """Return the print status message for the given object"""
    messages = {
        True: u'Must be printed',
        False: u'Should not be printed',
        None: u'Not convertible to a printable format',
    }
    if obj:
        return messages.get(obj.to_print, getattr(obj, 'to_print_message', ''))
    else:
        return messages[to_print_value]


def confidential_message(obj=None, confidential_value=None):
    """Return the confidential status message for the given object"""
    messages = {
        True: u'Element is confidential',
        False: u'Element is not confidential',
    }
    if obj:
        return messages.get(getattr(obj, 'confidential', None), '')
    else:
        return messages[confidential_value]


def signed_message(obj=None, to_sign_value=None, signed_value=None):
    """Return the signed message for the given object"""
    messages = {
        False: u'Element must be signed but is still not',
        True: u'Element is signed',
    }
    not_to_sign_msg = u'Element should not be signed'
    if obj:
        if getattr(obj, 'to_sign', False) is False:
            return not_to_sign_msg
        return messages.get(getattr(obj, 'signed', False), '')
    elif to_sign_value is False:
        return not_to_sign_msg
    else:
        return messages[signed_value]


@ram.cache(lambda f, p: (p, time() // (60 * 60)))
def is_file_type(portal_type):
    """Verify if the given portal type provides IFile or IImage"""
    portal_type = api.portal.get_tool('portal_types')[portal_type]
    module_path, classname = (
        u'.'.join(portal_type.klass.split('.')[:-1]),
        portal_type.klass.split('.')[-1],
    )
    module = __import__(module_path, {}, {}, [classname])
    cls = getattr(module, classname, None)
    if cls is None:
        return False
    for interface in (IFile, IImage):
        if cls.__implemented__(interface):
            return True
    return False
