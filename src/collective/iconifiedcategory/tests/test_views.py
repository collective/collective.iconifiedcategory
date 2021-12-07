# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective import iconifiedcategory as collective_iconifiedcategory
from collective.iconifiedcategory.tests.base import BaseTestCase
from collective.iconifiedcategory.utils import get_category_object
from plone import api
from Products.Five import zcml


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
        category = get_category_object(self.portal.file_txt,
                                       self.portal.file_txt.content_category)
        scale = category.restrictedTraverse('@@images').scale(scale='listing').__name__
        # the category and elements of category is displayed
        result = self.view()
        self.assertTrue(
            u'<img src="http://nohost/plone/config/group-1/category-1-1/@@images/{0}"'.format(scale)
            in result)

        # remove the categorized elements
        api.content.delete(self.portal['file_txt'])
        api.content.delete(self.portal['image'])
        api.content.delete(self.portal['docB'])
        api.content.delete(self.portal['docA'])
        self.assertEqual(self.view().strip(), u'<span class="discreet">Nothing.</span>')

    def test_categories_infos(self):
        self.view()
        infos = self.view.categories_infos()
        self.assertEqual(2, len(infos))
        self.assertEqual('category-1-1', infos[1]['id'])
        self.assertEqual(2, infos[0]['counts'])


class TestCategorizedChildInfosView(TestCategorizedChildView):

    def setUp(self):
        super(TestCategorizedChildInfosView, self).setUp()
        self.viewinfos = self.portal.restrictedTraverse('@@categorized-childs-infos')
        category_uid = self.config['group-1']['category-1-1'].UID()
        self.viewinfos(category_uid, filters={})

    def test__call__(self):
        # the category and elements of category is displayed
        self.viewinfos.update()
        result = self.viewinfos.index()
        self.assertTrue('<a class="categorized-element-title" href="http://nohost/plone/image/@@download">' in result)
        self.assertTrue('<span title="File description">file.txt</span>' in result)
        self.assertTrue(u'<a class="categorized-element-title" href="http://nohost/plone/image/@@download">' in result)
        self.assertTrue(u'<span title="Image description">ic\xf4ne1.png</span>' in result)

        # in case a file is too large, a warning is displayed
        # manipulate stored categorized_elements
        self.portal.categorized_elements[self.portal['file_txt'].UID()]['warn_filesize'] = True
        self.portal.categorized_elements[self.portal['file_txt'].UID()]['filesize'] = 7000000
        self.viewinfos.update()
        self.assertTrue("(<span class=\'warn_filesize\' title=\'Annex size is huge, "
                        "it could be difficult to be downloaded!\'>6.7 MB</span>)" in self.viewinfos.index())

        # remove the categorized elements
        api.content.delete(self.portal['file_txt'])
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

    def test_filters(self):
        self.viewinfos.update()
        self.assertEqual(len(self.viewinfos.categorized_elements), 2)
        self.viewinfos.filters['id'] = 'file_txt'
        self.viewinfos.update()
        self.assertEqual(len(self.viewinfos.categorized_elements), 1)
        self.assertEqual(self.viewinfos.categorized_elements[0]['id'], 'file_txt')
        # filters are passed to viewinfos as json
        self.viewinfos(category_uid=self.viewinfos.category_uid,
                       filters={"id": "image"})
        self.assertEqual(len(self.viewinfos.categorized_elements), 1)
        self.assertEqual(self.viewinfos.categorized_elements[0]['id'], 'image')


class TestCanViewAwareDownload(BaseTestCase):

    def test_default(self):
        # by default @@download returns the file, here
        # it is also the case as IIconifiedContent.can_view adapter returns True by default
        file_obj = self.portal['file_txt']
        img_obj = self.portal['image']
        self.assertTrue(file_obj.restrictedTraverse('@@download')())
        self.assertTrue(file_obj.restrictedTraverse('@@display-file')())
        self.assertTrue(file_obj.unrestrictedTraverse('view/++widget++form.widgets.file/@@download')())
        self.assertTrue(img_obj.restrictedTraverse('@@download')())
        self.assertTrue(img_obj.restrictedTraverse('@@display-file')())
        self.assertTrue(img_obj.unrestrictedTraverse('view/++widget++form.widgets.image/@@download')())

    def test_can_not_view(self):
        # register an adapter that will return False
        zcml.load_config('testing-adapters.zcml', collective_iconifiedcategory)
        file_obj = self.portal['file_txt']
        img_obj = self.portal['image']
        # downloadable when element is not confidential
        self.assertFalse(file_obj.confidential)
        self.assertFalse(img_obj.confidential)
        self.assertTrue(file_obj.restrictedTraverse('@@download')())
        self.assertTrue(file_obj.restrictedTraverse('@@display-file')())
        self.assertTrue(file_obj.unrestrictedTraverse('view/++widget++form.widgets.file/@@download')())
        self.assertTrue(img_obj.restrictedTraverse('@@download')())
        self.assertTrue(img_obj.restrictedTraverse('@@display-file')())
        self.assertTrue(img_obj.unrestrictedTraverse('view/++widget++form.widgets.image/@@download')())
        # when confidential, check can_view is done
        file_obj.confidential = True
        img_obj.confidential = True
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse('@@download'))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse('@@display-file'))
        self.assertRaises(Unauthorized, file_obj.unrestrictedTraverse('view/++widget++form.widgets.file/@@download'))
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse('@@download'))
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse('@@display-file'))
        self.assertRaises(Unauthorized, img_obj.unrestrictedTraverse('view/++widget++form.widgets.image/@@download'))
        # cleanUp zmcl.load_config because it impact other tests
        zcml.cleanUp()
