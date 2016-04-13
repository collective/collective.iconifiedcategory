# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone import api
from plone import namedfile
from plone.app.testing import login
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from zope.interface import alsoProvides

import os
import unittest

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
        api.content.create(
            id='image',
            type='Image',
            image=self.image,
            container=self.portal,
            content_category='config_-_group-1_-_category-1-1_-_subcategory-1-1-1',
            to_print=False,
            confidential=False,
        )

    def tearDown(self):
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])

    def test_category(self):
        file_adapter = adapter.CategorizedObjectInfoAdapter(self.portal['file'])
        self.assertEqual('config_-_group-1_-_category-1-1', file_adapter._category)

        image_adapter = adapter.CategorizedObjectInfoAdapter(self.portal['image'])
        self.assertEqual('config_-_group-1_-_category-1-1', image_adapter._category)

    def test_filesize(self):
        image_adapter = adapter.CategorizedObjectInfoAdapter(self.portal['image'])
        self.assertEqual(3742, image_adapter._filesize)

        file_adapter = adapter.CategorizedObjectInfoAdapter(self.portal['file'])
        self.assertEqual(3017, file_adapter._filesize)


class TestCategorizedObjectPrintableAdapter(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    @property
    def obj(self):
        return type('obj', (object, ), {
            'to_print': True,
            'file': type('file', (object, ), {'contentType': 'image/png'})(),
        })()

    def test_is_printable_default(self):
        obj = self.obj
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_is_printable_link(self):
        obj = self.obj
        alsoProvides(obj, ILink)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertFalse(print_adapter.is_printable)

    def test_is_printable_image(self):
        obj = self.obj
        alsoProvides(obj, IImage)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_is_printable_file(self):
        obj = self.obj
        alsoProvides(obj, IFile)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_verify_mimetype(self):
        obj = self.obj
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.verify_mimetype(obj.file))

        obj.file.contentType = 'text/rst'
        self.assertTrue(print_adapter.verify_mimetype(obj.file))

        obj.file.contentType = 'audio/mpeg3'
        self.assertFalse(print_adapter.verify_mimetype(obj.file))

        obj.file.contentType = 'application/pdf'
        self.assertTrue(print_adapter.verify_mimetype(obj.file))

    def test_update_object(self):
        obj = self.obj
        alsoProvides(obj, IFile)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        print_adapter.update_object()
        self.assertIsNone(obj.to_print_message)
        self.assertTrue(obj.to_print)

        obj.file.contentType = 'audio/mpeg3'
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        print_adapter.update_object()
        self.assertEqual(u'Can not be printed', obj.to_print_message)
        self.assertFalse(obj.to_print)
