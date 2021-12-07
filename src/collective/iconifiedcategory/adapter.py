# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_base
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.settings import Settings
from collective.documentviewer.utils import allowedDocumentType
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.subcategory import ISubcategory
from collective.iconifiedcategory.interfaces import IIconifiedPreview
from collective.iconifiedcategory.utils import _modified
from datetime import datetime
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.indexer.interfaces import IIndexableObject
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter


class CategorizedObjectInfoAdapter(object):

    def __init__(self, context):
        self.obj = aq_base(context)
        self.context = context

    def _get_basic_infos(self, category):
        """Return the basic informations for the object"""
        infos = {
            'category_uid': category.category_uid,
            'category_id': category.category_id,
            'category_title': category.category_title,
            'subcategory_uid': None,
            'subcategory_id': None,
            'subcategory_title': None,
            # this will be useable for caching for example
            'last_updated': self._last_updated,
            'icon_url': utils.get_category_icon_url(category),
            'to_be_printed_activated': self._to_be_printed_activated(category),
            'confidentiality_activated': self._confidentiality_activated(category),
            'signed_activated': self._signed_activated(category),
            'publishable_activated': self._publishable_activated(category),
            'to_print': self._to_print,
            'confidential': self._confidential,
            'to_sign': self._to_sign,
            'signed': self._signed,
            'publishable': self._publishable,
        }
        # update subcategory infos if any
        if ISubcategory.providedBy(category):
            infos['subcategory_uid'] = category.UID()
            infos['subcategory_id'] = category.getId()
            infos['subcategory_title'] = category.Title()
        return infos

    def get_infos(self, category, limited=False):
        filesize = self._filesize
        portal_url = api.portal.get_tool('portal_url')
        base_infos = self._get_basic_infos(category)
        if limited is True:
            return base_infos
        infos = {
            'title': self.obj.Title(),
            'description': self.obj.Description(),
            'id': self.obj.getId(),
            'relative_url': portal_url.getRelativeUrl(self.context),
            'download_url': self._download_url,
            'portal_type': self.obj.portal_type,
            'filesize': filesize,
            'warn_filesize': utils.warn_filesize(filesize),
            'preview_status': self._preview_status,
            'allowedRolesAndUsers': self._allowedRolesAndUsers,
        }
        infos.update(base_infos)
        return infos

    @property
    def _category(self):
        """Return the category instead of the subcategory"""
        return '_-_'.join(self.obj.content_category.split('_-_')[:3])

    @property
    def _download_url(self):
        """Return the download url (None by default) for the current object"""
        url = u'{url}/@@download'
        portal_url = api.portal.get_tool('portal_url')
        if IFile.providedBy(self.obj):
            return url.format(
                url=portal_url.getRelativeUrl(self.context))
        if IImage.providedBy(self.obj):
            return url.format(
                url=portal_url.getRelativeUrl(self.context))

    @property
    def _filesize(self):
        """Return the filesize if the contenttype is a File or an Image"""
        if IFile.providedBy(self.obj):
            return self.obj.file.size
        if IImage.providedBy(self.obj):
            return self.obj.image.size

    @property
    def _last_updated(self):
        """When updating some attributes directly or annotation,
           "modified" is not changed."""
        return _modified(self.context)

    def _to_be_printed_activated(self, category):
        category_group = category.get_category_group()
        return category_group.to_be_printed_activated

    @property
    def _to_print(self):
        return getattr(self.obj, 'to_print', False)

    def _confidentiality_activated(self, category):
        category_group = category.get_category_group()
        return category_group.confidentiality_activated

    @property
    def _confidential(self):
        return getattr(self.obj, 'confidential', False)

    def _signed_activated(self, category):
        category_group = category.get_category_group()
        return category_group.signed_activated

    @property
    def _to_sign(self):
        return getattr(self.obj, 'to_sign', False)

    @property
    def _signed(self):
        return getattr(self.obj, 'signed', False)

    def _publishable_activated(self, category):
        category_group = category.get_category_group()
        return category_group.publishable_activated

    @property
    def _publishable(self):
        return getattr(self.obj, 'publishable', False)

    @property
    def _preview_status(self):
        return IIconifiedPreview(self.obj).status

    @property
    def _allowedRolesAndUsers(self):
        catalog = api.portal.get_tool('portal_catalog')
        # use self.context that is acquisition wrapped, need this to get every local_roles
        wrapper = queryMultiAdapter((self.context, catalog, ), IIndexableObject)
        return wrapper.allowedRolesAndUsers


class CategorizedObjectPrintableAdapter(object):

    def __init__(self, context):
        self.context = context

    @property
    def is_printable(self):
        if ILink.providedBy(self.context):
            return False
        if IFile.providedBy(self.context):
            return IIconifiedPreview(self.context).is_convertible()
        if IImage.providedBy(self.context):
            return True
        return True

    @property
    def error_message(self):
        return u'Can not be printed'

    def update_object(self):
        self.context.to_print_message = None
        if self.is_printable is False:
            # None means 'deactivated'
            self.context.to_print = None
            self.context.to_print_message = self.error_message


class CategorizedObjectAdapter(object):

    def __init__(self, context, request, categorized_obj):
        self.context = context
        self.request = request
        self.categorized_obj = categorized_obj

    def can_view(self):
        """By default, check that current user may View the context.
           Indeed for some advanced management (@@download), views are
           declared permission="zope2.Public"."""
        if _checkPermission(View, self.context):
            return True


class CategorizedObjectPreviewAdapter(object):
    """Base adapter to verify the preview conversion status"""

    def __init__(self, context):
        self.context = context

    @property
    def status(self):
        """
          Returns the conversion status of context.
        """
        # not_convertable or awaiting conversion?
        if not self.is_convertible():
            return 'not_convertable'

        # under conversion?
        ann = IAnnotations(self.context)['collective.documentviewer']
        if 'successfully_converted' not in ann:
            if 'filehash' in ann:
                return 'in_progress'
            return 'not_converted'

        if not ann['successfully_converted'] is True:
            return 'conversion_error'

        return 'converted'

    @property
    def converted(self):
        """ """
        return self.status == 'converted'

    def is_convertible(self):
        """
          Check if the context is convertible (hopefully).
        """
        # collective.documentviewer add an entry to the annotations
        annotations = IAnnotations(self.context)
        if 'collective.documentviewer' not in annotations.keys():
            Settings(self.context)

        settings = GlobalSettings(api.portal.get())
        return allowedDocumentType(self.context,
                                   settings.auto_layout_file_types)


class IconifiedCategoryGroupAdapter(object):

    def __init__(self, config, context):
        self.config = config
        self.context = context

    def get_group(self):
        return self.config

    def get_every_categories(self, only_enabled=True):
        return utils.get_categories(self.context, only_enabled=only_enabled)
