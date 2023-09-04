# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collections import OrderedDict
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from plone.dexterity.utils import createContentInContainer
from zExceptions import Redirect

import transaction


class TestUtils(BaseTestCase):

    def setUp(self):
        super(TestUtils, self).setUp()
        elements = ('file_txt', 'image')
        for element in elements:
            if element in self.portal:
                api.content.delete(self.portal[element])

    def test_category_before_remove(self):
        """
        Ensure that an error is raised if we try to remove an used category
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        document = api.content.create(
            type='Document',
            title='doc-category-remove',
            container=self.portal,
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.delete, category)
        api.content.delete(document)
        api.content.delete(category)

    def test_category_before_remove_while_removing_plone_site(self):
        """
        Removing the Plone Site is not prohibited if categories exist.
        """
        app = self.portal.aq_inner.aq_parent
        self.assertEqual(self.portal.getId(), 'plone')
        self.assertTrue('plone' in app.objectIds())
        app.manage_delObjects(ids=['plone'])
        self.assertFalse('plone' in app.objectIds())

    def test_category_with_subcategory_before_remove(self):
        """
        Ensure that an error is raised if we try to remove a category that
        contains an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-category-remove-2',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.delete, category)
        api.content.delete(document)
        api.content.delete(category)

    def test_subcategory_before_removed(self):
        """
        Ensure that an error is raised if we try to remove an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        subcategory = api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-subcategory-remove',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.delete, subcategory)
        api.content.delete(document)
        api.content.delete(subcategory)
        api.content.delete(category)

    def test_category_moved(self):
        """
        Ensure that an error is raised if we try to move an used category
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        document = api.content.create(
            type='Document',
            title='doc-category-move-1',
            container=self.portal,
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.move, category,
                          self.config['group-2'])
        api.content.delete(document)
        category = api.content.move(category, self.config['group-2'])
        api.content.delete(category)

    def test_category_subcategory_moved(self):
        """
        Ensure that an error is raised if we try to move a category that
        contains an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-category-move-2',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        new_folder = self.config['group-1']
        self.assertRaises(Redirect, api.content.move, category, new_folder)
        api.content.delete(document)
        category = api.content.move(category, new_folder)
        api.content.delete(category)

    def test_subcategory_moved(self):
        """
        Ensure that an error is raised if we try to move an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        subcategory = api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-subcategory-move',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        new_folder = self.config['group-1']['category-1-1']
        self.assertRaises(Redirect, api.content.move, subcategory, new_folder)
        api.content.delete(document)
        subcategory = api.content.move(subcategory, new_folder)
        api.content.delete(subcategory)
        api.content.delete(category)

    def test_calculate_filesize(self):
        self.assertEqual('100 B', utils.calculate_filesize(100))
        self.assertEqual('1 KB', utils.calculate_filesize(1024))
        self.assertEqual('1.1 MB', utils.calculate_filesize(1150976))
        self.assertEqual('15.5 MB', utils.calculate_filesize(16252928))

    def test_print_message(self):
        obj = type('obj', (object, ), {
            'to_print': False,
        })()
        self.assertEqual(u'Should not be printed', utils.print_message(obj))

        obj.to_print = True
        self.assertEqual(u'Must be printed', utils.print_message(obj))

        obj.to_print = None
        self.assertEqual(u'Not convertible to a printable format',
                         utils.print_message(obj))

    def test_boolean_message(self):
        obj = type('obj', (object, ), OrderedDict())()
        self.assertEqual(u'', utils.boolean_message(obj))

        obj.confidential = True
        self.assertEqual(
            u'Element is confidential',
            utils.boolean_message(obj, attr_name='confidential'))
        obj.publishable = True
        self.assertEqual(
            u'Element is publishable',
            utils.boolean_message(obj, attr_name='publishable'))

        obj.confidential = False
        self.assertEqual(
            u'Element is not confidential',
            utils.boolean_message(obj, attr_name='confidential'))
        obj.publishable = False
        self.assertEqual(
            u'Element is not publishable',
            utils.boolean_message(obj, attr_name='publishable'))

    def test_warn_filesize(self):
        # default warning is for files > 5Mb
        self.assertEqual(
            api.portal.get_registry_record(
                'filesizelimit',
                interface=IIconifiedCategorySettings,
            ),
            5000000)
        file1 = api.content.create(
            id='file1',
            type='File',
            file=self.file,
            container=self.portal,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        self.assertEqual(file1.file.size, 3017)
        self.assertFalse(utils.warn_filesize(file1.file.size))

        # now enable warning (a specific portal_message is added when file created)
        api.portal.set_registry_record(
            'filesizelimit',
            interface=IIconifiedCategorySettings,
            value=3000)
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        self.assertEqual(file2.file.size, 3017)
        self.assertTrue(utils.warn_filesize(file2.file.size))

    def test_render_filesize(self):
        self.assertEqual(utils.render_filesize(1000),
                         '1000 B')
        self.assertEqual(utils.render_filesize(1024),
                         '1 KB')
        self.assertEqual(utils.render_filesize(5000),
                         '4 KB')
        # soft warning if filesize no more in B/KB
        self.assertEqual(utils.render_filesize(2500000),
                         u"<span class='soft_warn_filesize'>2.4 MB</span>")
        self.assertEqual(utils.render_filesize(5000000),
                         u"<span class='soft_warn_filesize'>4.8 MB</span>")
        # warning if filesize > 5000000
        self.assertEqual(utils.render_filesize(5000001),
                         u"<span class='warn_filesize' title='Annex size is huge, "
                         "it could be difficult to be downloaded!'>4.8 MB</span>")

    def test_get_categorized_elements(self):
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        transaction.commit()
        document = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc-subcategory-move',
            description='Document description',
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        scale = category.restrictedTraverse('@@images').scale(scale='listing').__name__
        # while creating, modified is changed again after categorized_update
        utils.update_all_categorized_elements(self.portal)
        result = utils.get_categorized_elements(self.portal)
        self.assertEqual(
            result,
            [{'UID': document.UID(),
              'allowedRolesAndUsers': ['Anonymous'],
              'category_id': 'category-x',
              'category_title': 'Category X',
              'category_uid': category.UID(),
              'confidential': False,
              'confidentiality_activated': False,
              'contentType': None,
              'description': 'Document description',
              'download_url': None,
              'filesize': None,
              'icon_url': u'config/group-1/category-x/@@images/{0}'.format(scale),
              'id': 'doc-subcategory-move',
              'last_updated': self._modified(document),
              'portal_type': 'Document',
              'preview_status': 'not_convertable',
              'publishable': False,
              'publishable_activated': False,
              'relative_url': 'doc-subcategory-move',
              'show_preview': 0,
              'signed': False,
              'signed_activated': False,
              'subcategory_id': None,
              'subcategory_title': None,
              'subcategory_uid': None,
              'title': 'doc-subcategory-move',
              'to_be_printed_activated': True,
              'to_print': False,
              'to_sign': False,
              'warn_filesize': False}])
        # filter on portal_type
        self.assertEqual(
            utils.get_categorized_elements(self.portal,
                                           portal_type='Document'),
            result)
        self.failIf(utils.get_categorized_elements(self.portal,
                                                   portal_type='Document2'))
        # ask the objects
        self.assertEqual(
            utils.get_categorized_elements(self.portal,
                                           result_type='objects'),
            [document])

        # sort_on
        document2 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='2doc-subcategory-move',
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        # result_type='dict'
        result = utils.get_categorized_elements(self.portal, sort_on='title')
        expected = [res['title'] for res in result]
        self.assertEqual(expected, ['2doc-subcategory-move', 'doc-subcategory-move'])

        # result_type='objects'
        self.assertEqual(
            set(utils.get_categorized_elements(self.portal,
                                               result_type='objects')),
            set([document, document2]))
        self.assertEqual(
            utils.get_categorized_elements(self.portal,
                                           result_type='objects',
                                           sort_on='title'),
            [document2, document])
        # sort_on='getObjPositionInParent'
        self.assertEqual(
            [elt['UID'] for elt in
             utils.get_categorized_elements(self.portal,
                                            result_type='dict',
                                            sort_on='getObjPositionInParent')],
            [document.UID(), document2.UID()])
        # change document position
        self.portal.folder_position(position='up', id=document2.getId())
        # sort_on='getObjPositionInParent'
        self.assertEqual(
            [elt['UID'] for elt in
             utils.get_categorized_elements(self.portal,
                                            result_type='dict',
                                            sort_on='getObjPositionInParent')],
            [document2.UID(), document.UID()])

        # teardown
        self.assertRaises(Redirect, api.content.delete, category)
        api.content.delete(document)
        api.content.delete(document2)
        api.content.delete(category)

    def test_get_categorized_elements_filters(self):
        self.config.get('group-1').confidentiality_activated = True
        createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='Doc1',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=True,
        )
        self.assertEqual(len(utils.get_categorized_elements(
            self.portal, filters={'confidential': True})),
            1)
        self.assertEqual(len(utils.get_categorized_elements(
            self.portal, filters={'confidential': False})),
            0)

    def test_update_categorized_elements(self):
        document2 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='CV Info N\xc2\xb02016-2',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        document3 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='CV Info N\xc2\xb02016-1',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        document10 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc10',
            content_category='config_-_group-1_-_category-1-2',
            to_print=False,
            confidential=False,
        )
        document1 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc1',
            content_category='config_-_group-1_-_category-1-2',
            to_print=False,
            confidential=False,
        )
        document4 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='Doc4',
            content_category='config_-_group-1_-_category-1-2',
            to_print=False,
            confidential=False,
        )

        self.assertEqual(
            [cat.id for cat in utils.get_categories(document1, the_objects=True)],
            ['category-1-3', 'category-2-3', 'category-1-2',
             'category-2-2', 'category-1-1', 'category-2-1']
        )

        # order is respected, by category
        result = ['doc1', 'Doc4', 'doc10', 'CV Info N\xc2\xb02016-1', 'CV Info N\xc2\xb02016-2']
        self.assertEqual(
            result,
            [e['title'] for e in self.portal.categorized_elements.values()],
        )
        api.content.delete(document1)
        api.content.delete(document2)
        api.content.delete(document3)
        api.content.delete(document10)
        api.content.delete(document4)

    def test_update_all_categorized_elements(self):
        document1 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc1',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        document1UID = document1.UID()
        document2 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc2',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        document2UID = document2.UID()
        self.assertEqual(len(self.portal.categorized_elements), 2)
        self.assertTrue(document1UID in self.portal.categorized_elements)
        self.assertTrue(document2UID in self.portal.categorized_elements)
        self.portal.categorized_elements = OrderedDict()
        self.assertEqual(len(self.portal.categorized_elements), 0)
        utils.update_all_categorized_elements(self.portal)
        self.assertEqual(len(self.portal.categorized_elements), 2)
        self.assertTrue(document1UID in self.portal.categorized_elements)
        self.assertTrue(document2UID in self.portal.categorized_elements)

        # if a content_category is wrong, element is no more stored in categorized_elements
        document1.content_category = 'some_wrong_category_id'
        utils.update_all_categorized_elements(self.portal)
        self.assertEqual(len(self.portal.categorized_elements), 1)
        self.assertTrue(document2UID in self.portal.categorized_elements)

    def test_get_category_icon_url(self):
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        subcategory = api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            container=category,
        )
        transaction.commit()
        document = api.content.create(
            type='Document',
            title='doc-subcategory-remove',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )

        subcategory = utils.get_category_object(document, document.content_category)
        doc_icon_url = utils.get_category_icon_url(subcategory)
        category = subcategory.get_category()
        scale = category.restrictedTraverse('@@images').scale(scale='listing').__name__
        self.assertEqual(doc_icon_url, u'config/group-1/category-x/@@images/{0}'.format(scale))

    def test_get_ordered_categories(self):
        """Test that caching is behaving correctly."""
        # invalidated when new category added
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        category_uid = category.UID()
        self.assertTrue(category_uid in utils.get_ordered_categories(self.portal))
        # invalidated when category deleted
        api.content.delete(category)
        self.assertFalse(category_uid in utils.get_ordered_categories(self.portal))
        # invalidated when a category position changed
        res = sorted(utils.get_ordered_categories(self.portal).items())
        self.portal.config.get('group-1').moveObjectsDown('category-1-2')
        res_after_cat_position_changed = sorted(utils.get_ordered_categories(self.portal).items())
        self.assertNotEqual(res, res_after_cat_position_changed)
