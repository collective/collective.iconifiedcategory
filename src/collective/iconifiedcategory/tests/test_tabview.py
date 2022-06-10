# -*- coding: utf-8 -*-

from collections import OrderedDict
from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.documentviewer.settings import GlobalSettings
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.browser.tabview import CategorizedContent
from collective.iconifiedcategory.browser.tabview import PrintColumn
from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from Products.CMFCore.permissions import ModifyPortalContent
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestCategorizedTabView(BaseTestCase):

    def test_table_render(self):
        view = self.portal.restrictedTraverse('@@iconifiedcategory')
        result = view()
        self.assertTrue('<a href="http://nohost/plone/file_txt" ' in result)
        self.assertTrue('File description' in result)
        self.assertTrue('<a href="http://nohost/plone/image" ' in result)
        self.assertTrue('Image description' in result)
        self.assertTrue('<td class="td_cell_category-column">Category 1-1</td>' in result)

        # 'to_print' and 'confidential' related columns are displayed by default
        self.assertTrue('<th>To be printed</th>' in result)
        self.assertTrue('<th>Confidential</th>' in result)

        # when nothing to display
        api.content.delete(self.portal['file_txt'])
        api.content.delete(self.portal['image'])
        self.assertEqual(self.portal.categorized_elements, OrderedDict())
        self.assertTrue('No element to display.' in view())

    def test_table_render_special_chars(self):
        """Special chars used in :
           - element's title;
           - category title;
           - subcategory title."""
        category = api.content.create(
            type='ContentCategory',
            title='Category \xc3\xa0',
            icon=self.icon,
            container=self.portal.config['group-1'],
        )
        subcategory = api.content.create(
            type='ContentSubcategory',
            title='Subcategory \xc3\xa0',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='Document \xc3\xa0',
            container=self.portal,
            content_category=utils.calculate_category_id(category),
            to_print=False,
            confidential=False,
        )
        document2 = api.content.create(
            type='Document',
            title='Document \xc3\xa0',
            container=self.portal,
            content_category=utils.calculate_category_id(subcategory),
            to_print=False,
            confidential=False,
        )
        # make sure every elements are correctly registered in categorized_elements
        # it seems that registration is made before element's id is renamed...
        utils.update_all_categorized_elements(self.portal)
        view = self.portal.restrictedTraverse('@@iconifiedcategory')
        result = view()
        self.assertTrue(category.title in result)
        self.assertTrue(subcategory.title in result)
        self.assertTrue(document.title in result)
        self.assertTrue(document2.title in result)

    def test_table_render_when_preview_enabled(self):
        self.portal.portal_properties.site_properties.typesUseViewActionInListings = ()
        # enable collective.documentviewer so document is convertible
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        # initialize collective.documentviewer annotations on file
        file_obj = self.portal['file_txt']
        image_obj = self.portal['image']
        notify(ObjectModifiedEvent(file_obj))
        notify(ObjectModifiedEvent(image_obj))

        view = self.portal.restrictedTraverse('@@iconifiedcategory')
        result = view()
        # by default, images are not handled by collective.documentviewer
        self.assertTrue('<a href="http://nohost/plone/image" ' in result)
        self.assertTrue('<a href="http://nohost/plone/file_txt/documentviewer#document/p1" ' in result)

    def test_PrintColumn(self):
        table = self.portal.restrictedTraverse('@@iconifiedcategory')
        file_infos = utils.get_categorized_elements(
            self.portal, uids=[self.portal['file_txt'].UID()])
        categorized_content = CategorizedContent(self.portal, file_infos[0])
        obj = categorized_content.getObject()
        column = PrintColumn(self.portal, self.portal.REQUEST, table)
        # not convertible by default as c.documentviewer not enabled
        self.assertEqual(
            column.renderCell(categorized_content),
            u'<a href="#" '
            u'class="iconified-action deactivated" '
            u'alt="Not convertible to a printable format" '
            u'title="Not convertible to a printable format"></a>')
        self.assertIsNone(categorized_content.to_print)
        self.assertIsNone(obj.to_print)

        # enable collective.documentviewer so document is convertible
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        # enable to_print management in configuration
        category = utils.get_category_object(obj, obj.content_category)
        category_group = category.get_category_group(category)
        category_group.to_be_printed_activated = True
        category.to_print = False
        notify(ObjectModifiedEvent(obj))
        file_infos = utils.get_categorized_elements(
            self.portal, uids=[self.portal['file_txt'].UID()])
        categorized_content = CategorizedContent(self.portal, file_infos[0])
        self.assertFalse(categorized_content.to_print)
        self.assertFalse(obj.to_print)
        self.assertEqual(
            column.renderCell(categorized_content),
            u'<a href="http://nohost/plone/file_txt/@@iconified-print" '
            u'class="iconified-action editable" '
            u'alt="Should not be printed" '
            u'title="Should not be printed"></a>')

        # set to_print to True
        obj.to_print = True
        notify(ObjectModifiedEvent(obj))
        file_infos = utils.get_categorized_elements(
            self.portal, uids=[self.portal['file_txt'].UID()])
        categorized_content = CategorizedContent(self.portal, file_infos[0])
        self.assertTrue(categorized_content.to_print)
        self.assertTrue(obj.to_print)
        self.assertEqual(
            column.renderCell(categorized_content),
            u'<a href="http://nohost/plone/file_txt/@@iconified-print" '
            u'class="iconified-action active editable" '
            u'alt="Must be printed" '
            u'title="Must be printed"></a>')

        # if element is not editable, the 'editable' CSS class is not there
        obj.manage_permission(ModifyPortalContent, roles=[])
        notify(ObjectModifiedEvent(obj))
        self.assertEqual(column.renderCell(categorized_content),
                         u'<a href="http://nohost/plone/file_txt/@@iconified-print" '
                         u'class="iconified-action active" '
                         u'alt="Must be printed" title="Must be printed"></a>')
