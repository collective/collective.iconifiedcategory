# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.documentviewer.async import queueJob
from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.documentviewer.settings import GlobalSettings
from collective.iconifiedcategory import adapter
from collective.iconifiedcategory.content.subcategory import ISubcategory
from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.tests.base import BaseTestCase
from collective.iconifiedcategory.utils import get_category_object
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.namedfile.utils import stream_data
from time import sleep
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectModifiedEvent


class TestCategorizedObjectInfoAdapter(BaseTestCase):

    def test_get_infos_for_file(self):
        obj = self.portal['file_txt']
        file_adapter = adapter.CategorizedObjectInfoAdapter(
            obj)
        category = get_category_object(obj, obj.content_category)
        infos = file_adapter.get_infos(category)
        scale = category.restrictedTraverse('@@images').scale(scale='listing').__name__
        self.assertEqual(
            infos,
            {'allowedRolesAndUsers': ['Anonymous'],
             'category_id': category.category_id,
             'category_title': category.category_title,
             'category_uid': category.category_uid,
             'confidential': False,
             'confidentiality_activated': False,
             'contentType': 'text/plain',
             'description': obj.Description(),
             'download_url': u'file_txt/@@download',
             'filesize': 3017,
             'icon_url': u'config/group-1/category-1-1/@@images/{0}'.format(scale),
             'id': obj.getId(),
             'last_updated': self._modified(obj),
             'portal_type': obj.portal_type,
             'preview_status': 'not_convertable',
             'publishable': False,
             'publishable_activated': False,
             'relative_url': 'file_txt',
             'show_preview': 0,
             'signed': False,
             'signed_activated': False,
             'subcategory_id': None,
             'subcategory_title': None,
             'subcategory_uid': None,
             'title': obj.Title(),
             'to_be_printed_activated': True,
             'to_print': None,
             'to_sign': False,
             'warn_filesize': False})

    def test_get_infos_for_image(self):
        obj = self.portal['image']
        image_adapter = adapter.CategorizedObjectInfoAdapter(
            obj)
        # image use a subcategory
        subcategory = get_category_object(obj, obj.content_category)
        infos = image_adapter.get_infos(subcategory)
        category = subcategory.get_category()
        scale = category.restrictedTraverse('@@images').scale(scale='listing').__name__
        self.assertEqual(
            infos,
            {'allowedRolesAndUsers': ['Anonymous'],
             'category_id': subcategory.category_id,
             'category_title': subcategory.category_title,
             'category_uid': subcategory.category_uid,
             'confidential': False,
             'confidentiality_activated': False,
             'contentType': 'image/png',
             'description': obj.Description(),
             'download_url': u'image/@@download',
             'filesize': 3742,
             'icon_url': u'config/group-1/category-1-1/@@images/{0}'.format(scale),
             'id': obj.getId(),
             'last_updated': self._modified(obj),
             'portal_type': obj.portal_type,
             'preview_status': 'not_convertable',
             'publishable': False,
             'publishable_activated': False,
             'relative_url': 'image',
             'show_preview': 0,
             'signed': False,
             'signed_activated': False,
             'subcategory_id': subcategory.id,
             'subcategory_title': subcategory.Title(),
             'subcategory_uid': subcategory.UID(),
             'title': obj.Title(),
             'to_be_printed_activated': True,
             'to_print': False,
             'to_sign': False,
             'warn_filesize': False})

    def test_get_infos_with_subcategory(self):
        obj = self.portal['file_txt']
        file_adapter = adapter.CategorizedObjectInfoAdapter(
            obj)
        subcategory = self.portal.restrictedTraverse('config/group-1/category-1-1/subcategory-1-1-1')
        self.assertTrue(ISubcategory.providedBy(subcategory))
        infos = file_adapter.get_infos(subcategory)
        category = subcategory.get_category()
        scale = category.restrictedTraverse('@@images').scale(scale='listing').__name__
        self.assertEqual(
            infos,
            {'allowedRolesAndUsers': ['Anonymous'],
             'category_id': subcategory.category_id,
             'category_title': subcategory.category_title,
             'category_uid': subcategory.category_uid,
             'confidential': False,
             'confidentiality_activated': False,
             'contentType': 'text/plain',
             'description': obj.Description(),
             'download_url': u'file_txt/@@download',
             'filesize': 3017,
             'icon_url': u'config/group-1/category-1-1/@@images/{0}'.format(scale),
             'id': obj.getId(),
             'last_updated': self._modified(obj),
             'portal_type': obj.portal_type,
             'preview_status': 'not_convertable',
             'publishable': False,
             'publishable_activated': False,
             'relative_url': 'file_txt',
             'show_preview': 0,
             'signed': False,
             'signed_activated': False,
             'subcategory_id': subcategory.getId(),
             'subcategory_title': subcategory.Title(),
             'subcategory_uid': subcategory.UID(),
             'title': obj.Title(),
             'to_be_printed_activated': True,
             'to_print': None,
             'to_sign': False,
             'warn_filesize': False})

    def test_category(self):
        file_adapter = adapter.CategorizedObjectInfoAdapter(
            self.portal['file_txt'])
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
            self.portal['file_txt'])
        self.assertEqual(3017, file_adapter._filesize)

    def test_download_url(self):
        image = self.portal['image']
        image_adapter = adapter.CategorizedObjectInfoAdapter(image)
        image_download_url = image_adapter._download_url
        self.assertEqual(image_download_url, u'image/@@download')
        # element is really downloadable
        download_view = self.portal.restrictedTraverse(str(image_download_url))
        self.assertEqual(stream_data(image.image), download_view())

        file_obj = self.portal['file_txt']
        file_adapter = adapter.CategorizedObjectInfoAdapter(file_obj)
        file_download_url = file_adapter._download_url
        self.assertEqual(file_download_url, u'file_txt/@@download')
        # element is really downloadable
        download_view = self.portal.restrictedTraverse(str(file_download_url))
        self.assertEqual(stream_data(file_obj.file), download_view())

    def test_preview_status(self):
        image_adapter = adapter.CategorizedObjectInfoAdapter(
            self.portal['image'])
        self.assertEqual('not_convertable',
                         image_adapter._preview_status)

        file_adapter = adapter.CategorizedObjectInfoAdapter(
            self.portal['file_txt'])
        self.assertEqual('not_convertable',
                         file_adapter._preview_status)

    def test_uri_are_relative_to_portal(self):
        obj = self.portal['file_txt']
        file_adapter = adapter.CategorizedObjectInfoAdapter(
            obj)
        category = get_category_object(obj, obj.content_category)
        infos = file_adapter.get_infos(category)
        portal_url = self.portal.absolute_url()
        self.assertTrue(not infos['relative_url'].startswith(portal_url))
        self.assertTrue(not infos['download_url'].startswith(portal_url))
        self.assertTrue(not infos['icon_url'].startswith(portal_url))


class TestCategorizedObjectAdapter(BaseTestCase):

    def test_can_view(self):
        cat_adapter = getMultiAdapter((self.portal, self.portal.REQUEST, self.portal['file_txt']),
                                      IIconifiedContent)
        self.assertTrue(cat_adapter.can_view())


class TestCategorizedObjectPrintableAdapter(BaseTestCase):

    def setUp(self):
        super(TestCategorizedObjectPrintableAdapter, self).setUp()
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()

    def test_is_printable_default(self):
        obj = self.portal.file_txt
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_is_printable_link(self):
        obj = self.portal.file_txt
        alsoProvides(obj, ILink)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertFalse(print_adapter.is_printable)

    def test_is_printable_image(self):
        obj = self.portal.file_txt
        alsoProvides(obj, IImage)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_is_printable_file(self):
        obj = self.portal.file_txt
        alsoProvides(obj, IFile)
        print_adapter = adapter.CategorizedObjectPrintableAdapter(obj)
        self.assertTrue(print_adapter.is_printable)

    def test_update_object(self):
        obj = self.portal.file_txt
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


class TestCategorizedObjectPreviewAdapter(BaseTestCase):

    def test_is_convertible(self):
        obj = self.portal['file_txt']

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

    def test_status(self):
        obj = self.portal['file_txt']

        preview_adapter = adapter.CategorizedObjectPreviewAdapter(obj)

        gsettings = GlobalSettings(self.portal)
        self.assertEqual(gsettings.auto_layout_file_types, ['pdf'])

        obj.file.contentType = 'application/rtf'
        self.assertEqual(preview_adapter.status, 'not_convertable')
        self.assertFalse(preview_adapter.converted)

        obj.file.contentType = 'application/pdf'
        self.assertEqual(preview_adapter.status, 'not_converted')
        self.assertFalse(preview_adapter.converted)

        ann = IAnnotations(obj)['collective.documentviewer']
        ann['filehash'] = '--foobar--'
        obj.file.contentType = 'application/pdf'
        self.assertEqual(preview_adapter.status, 'in_progress')
        self.assertFalse(preview_adapter.converted)

        queueJob(obj)
        # not a real PDF actually...
        self.assertEqual(preview_adapter.status, 'conversion_error')
        self.assertFalse(preview_adapter.converted)

        # enable every supported types including txt
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        obj.file.contentType = 'text/plain'
        # collective.documentviewer checks if element was modified
        # or it does not convert again
        sleep(1)
        obj.notifyModified()
        queueJob(obj)
        self.assertEqual(preview_adapter.status, 'converted')
        self.assertTrue(preview_adapter.converted)
