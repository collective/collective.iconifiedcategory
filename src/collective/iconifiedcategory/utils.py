# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_base
from collections import OrderedDict
from collective.iconifiedcategory import _
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
from datetime import datetime
from imio.helpers.cache import get_cachekey_volatile
from imio.helpers.content import find
from natsort import natsorted
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.memoize import ram
from Products.CMFPlone.utils import safe_unicode
from time import time
from zope.annotation import IAnnotations
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import Invalid

import copy


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
        result = catalog.unrestrictedSearchResults(**query)
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
    }
    # query on path is context is not the Plone Site
    # happens when computing categories to generate CSS
    if context.portal_type != "Plone Site":
        query['path'] = '/'.join(config_group.getPhysicalPath())
    if only_enabled:
        query['enabled'] = True
    if sort_on:
        query['sort_on'] = sort_on

    res = catalog.unrestrictedSearchResults(**query)
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

    # do not use restrictedTraverse or getMultiAdapter to get the "@@images" view
    # because when used with plone.app.async, as there is no REQUEST, it fails.
    from collective.iconifiedcategory.browser.views import ImageDataModifiedImageScaling
    images = ImageDataModifiedImageScaling(obj, getattr(obj, 'REQUEST', None))
    scale = images.scale(scale='listing')

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
    adapter = None
    for obj in container.objectValues():
        if hasattr(obj, 'content_category'):
            try:
                category = get_category_object(obj, obj.content_category)
            except KeyError:
                continue
            if adapter is None:
                adapter = getAdapter(obj, IIconifiedInfos)
            else:
                adapter.context = obj
                adapter.obj = aq_base(obj)
            uid, new_infos = obj.UID(), adapter.get_infos(category, limited=limited)
            infos = container.categorized_elements.get(uid, {})
            infos.update(new_infos)
            container.categorized_elements[uid] = infos
    if container.categorized_elements and sort:
        sort_categorized_elements(container)


def get_ordered_categories_cachekey(method, context, only_enabled=True):
    """Makes cache depend on config root."""
    return (repr(get_config_root(context)),
            get_cachekey_volatile("collective.iconifiedcategory.utils.get_ordered_categories"))


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
        elements[category.UID()] = idx
        elements[calculate_category_id(category)] = idx
        subcategories = find(context=category, unrestricted=True, **query)
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
        getattr(aq_base(context), 'categorized_elements', OrderedDict())
    )


def _check_filters(infos, filters):
    """ """
    keep = True
    for k, v in filters.items():
        # manage case when stored value is a list or not
        stored_value = infos[k]
        if not hasattr(stored_value, '__iter__'):
            stored_value = (stored_value, )
        if v not in stored_value:
            keep = False
            break
    return keep


def _get_adapter(context, obj, adapter):
    """ """
    if adapter is None:
        adapter = getMultiAdapter(
            (context, context.REQUEST, obj),
            IIconifiedContent)
    else:
        adapter.categorized_obj = obj
    return adapter


def get_categorized_elements(context,
                             result_type='dict',
                             portal_type=None,
                             sort_on=None,
                             uids=[],
                             filters={},
                             check_can_view=True,
                             caching=True):
    """Return categorized elements.
       p_result_type may be :
       - 'dict': default, essential metadata are returned as a dict;
       - 'objects': categorized objects are returned.
       If some p_filters are given, the values will be filtered,
       available filters are values stored in categorized_elements.
       If p_check_can_view is True, then the IIconifiedContent.can_view
       check will be called."""
    elements = None
    if caching:
        # in some cases like in tests, request can not be retrieved
        key = "collective.iconifiedcategory.get_categorized_elements'" \
            "-{0}-{1}-{2}-{3}-{4}".format(
                repr(context),
                result_type,
                portal_type,
                '_'.join(uids),
                ['{0}_{1}'.format(k, v) for k, v in filters.items()])
        cache = IAnnotations(context.REQUEST)
        elements = cache.get(key, None)

    if elements is None:
        elements = []
        categorized_elements = _categorized_elements(context)
        if not categorized_elements:
            return elements

        uids = uids or categorized_elements.keys()
        catalog = api.portal.get_tool('portal_catalog')
        current_user_allowedRolesAndUsers = catalog._listAllowedRolesAndUsers(api.user.get_current())
        adapter = None
        for uid, infos in categorized_elements.items():
            if (uids and uid not in uids) or \
               (portal_type and infos['portal_type'] != portal_type) or \
               not _check_filters(infos, filters) or \
               (infos['confidential'] and not set(infos['allowedRolesAndUsers'])
                   .intersection(current_user_allowedRolesAndUsers)):
                continue

            obj = context.get(infos['id'])
            adapter = _get_adapter(context, obj, adapter)
            if not check_can_view or adapter.can_view():
                if result_type == 'objects':
                    elements.append(obj)
                else:
                    # add 'UID' to the available infos
                    tmp = categorized_elements[uid].copy()
                    tmp['UID'] = uid
                    elements.append(tmp)

        if elements and sort_on:
            if result_type == 'dict':
                if sort_on in elements[0]:
                    elements = sorted(elements, key=lambda x, sort_on=sort_on: x[sort_on])
                elif sort_on == 'getObjPositionInParent':
                    elements = sorted(
                        elements,
                        key=lambda x, object_ids=context.objectIds(): object_ids.index(x['id']))
            else:
                if getattr(elements[0], sort_on):
                    elements = sorted(elements, key=lambda x, sort_on=sort_on: getattr(x, sort_on))
                elif sort_on == 'getObjPositionInParent':
                    elements = sorted(
                        elements,
                        key=lambda x, object_ids=context.objectIds(): object_ids.index(x.id))

    return elements


def get_back_references(obj):
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog.unrestrictedSearchResults(content_category_uid=obj.UID())
    return brains


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
    elif not pretty_filesize.endswith((' B', ' KB')):
        pretty_filesize = \
            u"<span class='soft_warn_filesize'>{0}</span>".format(pretty_filesize)
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


def boolean_message(obj=None, attr_name='', value=None):
    """Return the default boolean status message for the given object"""
    messages = {
        True: u'Element is {0}'.format(attr_name),
        False: u'Element is not {0}'.format(attr_name),
    }
    if obj:
        return messages.get(getattr(obj, attr_name, None), '')
    else:
        return messages[value]


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


def validateFileIsPDF(data):
    """May be used as helper in a invariant validator"""
    def _get_content_type(data):
        """ """
        contentType = getattr(data, 'contentType', None)
        if contentType is None:
            file = request.form.get('form.widgets.file') or \
                getattr(aq_base(context), 'file', None)
            # get contentType
            if file:
                contentType = getattr(file, 'contentType', None) or file.headers.get('content-type')
        return contentType

    # check if file contentType is PDF only if used content_category requires it
    request = getRequest()
    # avoid double validation
    if request.get('already_validateFileIsPDF', False):
        return
    request.set('already_validateFileIsPDF', True)
    context = data.__context__ or request.get('PUBLISHED').context
    contentType = _get_content_type(data)
    if contentType is not None and contentType != 'application/pdf':
        category = get_category_object(context, data.content_category)
        if category.only_pdf:
            raise Invalid(_(u"You must select a PDF file!"))


def _modified(obj, asdatetime=True):
    """Returns max value between obj.modified() and obj._p_mtime,
       in case an annotation is changed on obj, obj._p_mtime is changed,
       not obj.modified()."""
    modified = max(float(obj.modified()), obj._p_mtime)
    if asdatetime:
        modified = datetime.fromtimestamp(modified)
    return modified
