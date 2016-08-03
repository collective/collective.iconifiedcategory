# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_base
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink

from collective.iconifiedcategory import utils


class CategorizedObjectInfoAdapter(object):

    def __init__(self, context):
        self.obj = aq_base(context)
        self.context = context

    def get_infos(self, category):
        return {
            'title': self.obj.Title(),
            'id': self.obj.getId(),
            'category_uid': category.category_uid,
            'category_id': category.category_id,
            'category_title': category.category_title,
            'absolute_url': self.context.absolute_url(),
            'icon_url': utils.get_category_icon_url(category),
            'portal_type': self.obj.portal_type,
            'filesize': self._filesize,
            'to_print': self._to_print,
            'confidential': self._confidential,
        }

    @property
    def _category(self):
        """Return the category instead of the subcategory"""
        return '_-_'.join(self.obj.content_category.split('_-_')[:3])

    @property
    def _filesize(self):
        """Return the filesize if the contenttype is a File or an Image"""
        if IFile.providedBy(self.obj):
            return self.obj.file.size
        if IImage.providedBy(self.obj):
            return self.obj.image.size

    @property
    def _to_print(self):
        return getattr(self.obj, 'to_print', False)

    @property
    def _confidential(self):
        return getattr(self.obj, 'confidential', False)


class CategorizedObjectPrintableAdapter(object):

    def __init__(self, context):
        self.context = context

    @property
    def is_printable(self):
        if ILink.providedBy(self.context):
            return False
        if IFile.providedBy(self.context):
            return self.verify_mimetype(self.context.file)
        if IImage.providedBy(self.context):
            return True
        return True

    def verify_mimetype(self, file):
        extra_mimetypes = (
            'application/pdf',
            'application/plain',
            'application/msword',
            'application/excel',
        )
        mimetype = file.contentType
        if mimetype.split('/')[0] in ('image', 'text'):
            return True
        if file.contentType in extra_mimetypes:
            return True
        return False

    @property
    def error_message(self):
        return u'Can not be printed'

    def update_object(self):
        self.context.to_print_message = None
        if self.is_printable is False:
            self.context.to_print = None
            self.context.to_print_message = self.error_message


class CategorizedObjectAdapter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def can_view(self):
        return api.user.has_permission('View', obj=self.context)
