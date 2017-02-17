# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Products.Five import zcml
from plone import api
from collective import iconifiedcategory as collective_iconifiedcategory
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestCategorizedChildView(BaseTestCase):

    def setUp(self):
        super(TestCategorizedChildView, self).setUp()
        api.content.create(
            id='docB',
            type='Document',
            title='B',
            container=self.portal,
            content_category='config_-_group-1_-_category-1-2',
            to_print=False,
            confidential=False,
        )
        api.content.create(
            id='docA',
            type='Document',
            title='A',
            container=self.portal,
            content_category='config_-_group-1_-_category-1-2',
            to_print=False,
            confidential=False,
        )
        self.view = self.portal.restrictedTraverse('@@categorized-childs')
        self.view.portal_type = None

    def tearDown(self):
        super(TestCategorizedChildView, self).tearDown()
        elements = ('docB', 'docA')
        for element in elements:
            if element in self.portal:
                api.content.delete(self.portal[element])

    def test__call__(self):
        # the category and elements of category is displayed
        result = self.view()
        self.assertTrue(
            u'<img src="http://nohost/plone/config/group-1/category-1-1/@@download"'
            in result)

        # remove the categorized elements
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        api.content.delete(self.portal['docB'])
        api.content.delete(self.portal['docA'])
        self.assertEqual(self.view().strip(), u'<span class="discreet">Nothing.</span>')

    def test_categories_infos(self):
        self.view.update()
        infos = self.view.categories_infos()
        self.assertEqual(2, len(infos))
        self.assertEqual('category-1-1', infos[1]['id'])
        self.assertEqual(2, infos[0]['counts'])


class TestCategorizedChildInfosView(TestCategorizedChildView):

    def setUp(self):
        super(TestCategorizedChildInfosView, self).setUp()
        self.viewinfos = self.portal.restrictedTraverse('@@categorized-childs-infos')
        self.viewinfos.category_uid = self.config['group-1']['category-1-1'].UID()

    def test__call__(self):
        # the category and elements of category is displayed
        self.viewinfos.update()
        result = self.viewinfos.index()
        self.assertTrue('<a href="http://nohost/plone/file/@@download">' in result)
        self.assertTrue('<span title="File description">file.txt</span>' in result)
        self.assertTrue(u'<a href="http://nohost/plone/image/@@download">' in result)
        self.assertTrue(u'<span title="Image description">ic\xf4ne1.png</span>' in result)

        # in case a file is too large, a warning is displayed
        # manipulate stored categorized_elements
        self.portal.categorized_elements[self.portal['file'].UID()]['warn_filesize'] = True
        self.portal.categorized_elements[self.portal['file'].UID()]['filesize'] = 7000000
        self.viewinfos.update()
        self.assertTrue("(<span class=\'warn_filesize\' title=\'Annex size is huge, "
                        "it could be difficult to be downloaded!\'>6.7 MB</span>)" in self.viewinfos.index())

        # remove the categorized elements
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        api.content.delete(self.portal['docB'])
        api.content.delete(self.portal['docA'])
        self.viewinfos.update()
        self.assertEqual(self.viewinfos.index(), u'\n')

    def test_categories_uids(self):
        self.viewinfos.update()
        self.assertEqual(
            [self.viewinfos.category_uid],
            self.viewinfos.categories_uids,
        )
        self.viewinfos.category_uid = self.config['group-1']['category-1-2'].UID()
        self.viewinfos.update()
        self.assertEqual(
            [self.viewinfos.category_uid],
            self.viewinfos.categories_uids,
        )

    def test_infos(self):
        self.viewinfos.update()
        infos = self.viewinfos.infos()
        self.assertItemsEqual([self.viewinfos.category_uid], infos.keys())
        self.assertItemsEqual(
            ['file.txt', 'ic\xc3\xb4ne1.png'],
            [e['title'] for e in infos[self.viewinfos.category_uid]],
        )

        self.viewinfos.category_uid = self.config['group-1']['category-1-2'].UID()
        self.viewinfos.update()
        infos = self.viewinfos.infos()
        self.assertItemsEqual([self.viewinfos.category_uid], infos.keys())
        self.assertItemsEqual(
            ['A', 'B'],
            [e['title'] for e in infos[self.viewinfos.category_uid]],
        )


class TestCanViewAwareDownload(BaseTestCase):

    def test_default(self):
        # by default @@download returns the file, here
        # it is also the case as IIconifiedContent.can_view adapter returns True by default
        file_obj = self.portal['file']
        img_obj = self.portal['image']
        self.assertTrue(file_obj.restrictedTraverse('@@download')())
        self.assertTrue(file_obj.restrictedTraverse('@@display-file')())
        self.assertTrue(img_obj.restrictedTraverse('@@download')())
        self.assertTrue(img_obj.restrictedTraverse('@@display-file')())

    def test_can_not_view(self):
        # register an adapter that will return False
        zcml.load_config('testing-adapters.zcml', collective_iconifiedcategory)
        file_obj = self.portal['file']
        img_obj = self.portal['image']
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse('@@download'))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse('@@display-file'))
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse('@@download'))
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse('@@display-file'))
        # cleanUp zmcl.load_config because it impact other tests
        zcml.cleanUp()
