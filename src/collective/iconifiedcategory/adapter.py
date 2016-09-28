# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_base
from zope.annotation import IAnnotations
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink

import logging
logger = logging.getLogger('collective.iconifiedcategory')

from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.interfaces import IIconifiedPreview

from Products.MimetypesRegistry.common import MimeTypeException

MIME_TYPE_NOT_FOUND = 'The mime_type for annex at %s was not found in mimetypes_registry!'
FILE_EXTENSION_NOT_FOUND = 'The extension used by MeetingFile at %s does not correspond to ' \
    'an extension available in the mimetype %s found in mimetypes_registry!'


class CategorizedObjectInfoAdapter(object):

    def __init__(self, context):
        self.obj = aq_base(context)
        self.context = context

    def get_infos(self, category):
        filesize = self._filesize
        return {
            'title': self.obj.Title(),
            'id': self.obj.getId(),
            'category_uid': category.category_uid,
            'category_id': category.category_id,
            'category_title': category.category_title,
            'absolute_url': self.context.absolute_url(),
            'download_url': self._download_url,
            'icon_url': utils.get_category_icon_url(category),
            'portal_type': self.obj.portal_type,
            'filesize': filesize,
            'warn_filesize': utils.warn_filesize(filesize),
            'to_print': self._to_print,
            'confidential': self._confidential,
            'preview_status': self._preview_status,
        }

    @property
    def _category(self):
        """Return the category instead of the subcategory"""
        return '_-_'.join(self.obj.content_category.split('_-_')[:3])

    @property
    def _download_url(self):
        """Return the download url (None by default) for the current object"""
        url = u'{url}/@@download/{field}/{filename}'
        if IFile.providedBy(self.obj):
            return url.format(
                url=self.context.absolute_url(),
                field='file',
                filename=self.obj.file.filename,
            )
        if IImage.providedBy(self.obj):
            return url.format(
                url=self.context.absolute_url(),
                field='file',
                filename=self.obj.image.filename,
            )

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

    @property
    def _preview_status(self):
        return IIconifiedPreview(self.obj).status


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
        if file.contentType in IIconifiedPreview(self.context).convertible_mimetypes:
            return True
        return False

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

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def can_view(self):
        return api.user.has_permission('View', obj=self.context)


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
        if not self._isConvertible():
            return 'not_convertable'

        # under conversion?
        annotations = IAnnotations(self.context)
        if 'successfully_converted' not in annotations['collective.documentviewer']:
            return 'in_progress'

        if not annotations['collective.documentviewer']['successfully_converted'] is True:
            return 'conversion_error'

        return 'converted'

    @property
    def converted(self):
        """ """
        return self.status == 'converted'

    def _isConvertible(self):
        """
          Check if the context is convertible (hopefully).  If the mimetype is one taken into
          account by collective.documentviewer CONVERTABLE_TYPES, then it should be convertible...
        """
        # collective.documentviewer add an entry the annotations to relevant possibily convertible types
        annotations = IAnnotations(self.context)
        if 'collective.documentviewer' not in annotations.keys():
            return False

        # now check if current file mimetype is managed by collective.documentviewer
        mr = api.portal.get_tool('mimetypes_registry')
        try:
            mime_type = mr.lookup(self.context.file.contentType)[0]
        except MimeTypeException:
            mime_type = None
        if not mime_type:
            logger.warning(MIME_TYPE_NOT_FOUND % self.context.absolute_url_path())
            return False

        if set(mime_type.mimetypes).intersection(self.convertible_mimetypes):
            return True

        return False

    @property
    def convertible_mimetypes(self):
        """ """
        # we have convertible extensions in collective.documentviewer
        extensions = []
        for convertible_type in CONVERTABLE_TYPES.iteritems():
            extensions.extend(convertible_type[1].extensions)

        # now build a list of mimetypes
        mr = api.portal.get_tool('mimetypes_registry')
        mimetypes = []
        for extension in extensions:
            content_type = mr.lookupExtension(extension)
            if not content_type:
                continue
            for mtype in content_type.mimetypes:
                if not mtype in mimetypes:
                    mimetypes.append(mtype)
        return mimetypes


class IconifiedCategoryGroupAdapter(object):

    def __init__(self, config, context):
        self.config = config
        self.context = context

    def get_group(self):
        return self.config
