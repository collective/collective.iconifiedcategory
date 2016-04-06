# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink

from collective.iconifiedcategory import utils


class CategorizedObjectInfoAdapter(object):

    def __init__(self, context):
        self.context = context

    def get_infos(self, category):
        return {
            'title': self.context.Title(),
            'id': self.context.getId(),
            'category_uid': category.category_uid,
            'category_id': category.category_id,
            'category_title': category.category_title,
            'absolute_url': self.context.absolute_url(),
            'icon_url': utils.get_category_icon_url(category),
            'portal_type': self.context.portal_type,
            'filesize': self._filesize,
        }

    @property
    def _category(self):
        """Return the category instead of the subcategory"""
        return '_-_'.join(self.context.content_category.split('_-_')[:3])

    @property
    def _filesize(self):
        """Return the filesize if the contenttype is a File or an Image"""
        if IFile.providedBy(self.context):
            return self.context.file.size
        if IImage.providedBy(self.context):
            return self.context.image.size


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
