# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from plone import api
from plone import namedfile
from plone.app.testing import login
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from zope.interface import alsoProvides

import os
import unittest

from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.settings import Settings
from collective.iconifiedcategory import adapter
from collective.iconifiedcategory import testing


class TestCategorizedObjectInfoAdapter(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    @property
    def image(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'icon1.png'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'icon1.png')

    @property
    def file(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'file.txt'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'file.txt')

    def setUp(self):
        self.portal = self.layer['portal']
        api.user.create(
            email='test@test.com',
            username='adminuser',
            password='secret',
        )
        api.user.grant_roles(
            username='adminuser',
            roles=['Manager'],
        )
        login(self.portal, 'adminuser')
        api.content.create(
            id='file',
            type='File',
            file=self.file,
            container=self.portal,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        cat_id = 'config_-_group-1_-_category-1-1_-_subcategory-1-1-1'
        api.content.create(
            id='image',
            type='Image',
            image=self.image,
            container=self.portal,
            content_category=cat_id,
            to_print=False,
            confidential=False,
        )

    def tearDown(self):
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])

    def test_category(self):
        file_adapter = adapter.CategorizedObjectInfoAdapter(
            self.portal['file'])
        self.assertEqual('config_-_group-1_-_category-1-1',
                         file_adapter._category)

        image_adapter = adapter.CategorizedObjectInfoAdapter(
            self.portal['image'])
        self.assertEqual('config_-_group-1_-_category-1-1',
                         image_adapter._category)

    def test_filesize(self):
        image_adapter = adapter.CategorizedObjectInfoAdapter(
            self.portal['image'])
        self.assertEqual(3742, image_adapter._filesize)

        file_adapter = adapter.CategorizedObjectInfoAdapter(
            self.portal['file'])
        self.assertEqual(3017, file_adapter._filesize)


class TestCategorizedObjectPrintableAdapter(TestCategorizedObjectInfoAdapter):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestCategorizedObjectPrintableAdapter, self).setUp()
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()

        # initialize annotations on file
        obj = self.portal['file']
        Settings(obj)

    def test_is_printable_default(self):
        obj = self.portal.file
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_is_printable_link(self):
        obj = self.portal.file
        alsoProvides(obj, ILink)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertFalse(print_adapter.is_printable)

    def test_is_printable_image(self):
        obj = self.portal.file
        alsoProvides(obj, IImage)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_is_printable_file(self):
        obj = self.portal.file
        alsoProvides(obj, IFile)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_update_object(self):
        obj = self.portal.file
        alsoProvides(obj, IFile)
        # will be converted with collective.documentviewer
        obj.to_print = True
        notify(ObjectModifiedEvent(obj))
        self.assertIsNone(obj.to_print_message)
        self.assertTrue(obj.to_print)

        obj.file.contentType = 'audio/mpeg3'
        obj.to_print = True
        notify(ObjectModifiedEvent(obj))
        self.assertEqual(u'Can not be printed', obj.to_print_message)
        self.assertFalse(obj.to_print)


class TestCategorizedObjectPreviewAdapter(TestCategorizedObjectInfoAdapter):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def test_is_convertible(self):
        obj = self.portal['file']
        # initialize annotations on file
        Settings(obj)

        preview_adapter = adapter.CategorizedObjectPreviewAdapter(obj)

        # convertible relies on the fact that contentType is managed
        # by collective.documentviewer gsettings.auto_layout_file_types
        gsettings = GlobalSettings(self.portal)
        self.assertEqual(gsettings.auto_layout_file_types, ['pdf'])

        obj.file.contentType = 'application/pdf'
        self.assertTrue(preview_adapter.is_convertible())

        obj.file.contentType = 'application/rtf'
        self.assertFalse(preview_adapter.is_convertible())

        # right enable every file_types in collective.documentviewer
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()

        convertables = (
            'application/msword',
            'application/pdf',
            'application/rtf',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.oasis.opendocument.text',
            # xlsx
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'image/png',
            'image/jpeg',
            'text/html',
            )
        for convertable in convertables:
            obj.file.contentType = convertable
            self.assertTrue(preview_adapter.is_convertible())

        not_convertables = ('application/octet-stream',
                            'text/x-python')
        for not_convertable in not_convertables:
            obj.file.contentType = not_convertable
            self.assertFalse(preview_adapter.is_convertible())
