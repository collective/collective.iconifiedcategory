# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

import logging
logger = logging.getLogger('collective.iconifiedcategory')

from zope.annotation import IAnnotations
from zope.globalrequest import getRequest
from plone import api
from Products.MimetypesRegistry.common import MimeTypeException

CONTENT_TYPE_NOT_FOUND = 'The content_type for MeetingFile at %s was not found in mimetypes_registry!'
FILE_EXTENSION_NOT_FOUND = 'The extension used by MeetingFile at %s does not correspond to ' \
    'an extension available in the mimetype %s found in mimetypes_registry!'


class PreviewStatus(object):
    """
    Preview status class

    Valid status codes are:
        * not_convertible
        * in_progress
        * converted
        * conversion_error
    """
    _valid_codes = (
        'not_convertible',
        'in_progress',
        'converted',
        'conversion_error',
    )

    def __init__(self, context):
        self.context = context
        self.request = getRequest()

    def get_status(self):
        """
          Returns the conversion status of context.
          Status can be :
          - not_convertible : the context is not convertable by collective.documentviewer
          - in_progress : or awaiting conversion, the context is convertable but is not yet converted
          - conversion_error : there was an error during conversion.
                               Manager have access in the UI to more infos.
          - converted : the context is converted correctly
        """
        # not_convertable or awaiting conversion?
        if not self._isConvertible(self.context):
            return 'not_convertable'

        # under conversion?
        annotations = IAnnotations(self.context)
        if 'successfully_converted' not in annotations['collective.documentviewer']:
            return 'in_progress'

        if not annotations['collective.documentviewer']['successfully_converted'] is True:
            return 'conversion_error'

        return 'converted'

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
            content_type = mr.lookup(self.context.content_type)
        except MimeTypeException:
            content_type = None
        if not content_type:
            logger.warning(CONTENT_TYPE_NOT_FOUND % self.context.absolute_url_path())
            return False
        # get printable extensions from collective.documentviewer
        printableExtensions = self._documentViewerPrintableExtensions()

        # mr.lookup returns a list
        extensions = content_type[0].extensions
        # now that we have the extensions, find the one we are using
        currentExtension = ''
        # in case we have myimage.JPG, make sure extension is lowercase as
        # extentions on mimetypes_registry are lowercase...
        filename = self.context.file.filename
        file_extension = filename.split('.')[-1].lower()
        for extension in extensions:
            if file_extension == extension:
                currentExtension = extension
                break

        # if we found the exact extension we are using, we can see if it is in the list
        # of printable extensions provided by collective.documentviewer
        # most of times, this is True...
        if currentExtension in printableExtensions:
            return True
        if not currentExtension:
            logger.warning(FILE_EXTENSION_NOT_FOUND % (self.context.absolute_url_path(),
                                                       content_type[0]))

        # if we did not find the currentExtension in the mimetype's extensions,
        # for example an uploaded element without extension, check nevertheless
        # if the mimetype seems to be managed by collective.documentviewer
        if set(extensions).intersection(set(printableExtensions)):
            return True

        return False
