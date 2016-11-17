# -*- coding: utf-8 -*-

import lxml
from AccessControl import Unauthorized
from Products.Five import zcml
from plone import api
from collective import iconifiedcategory as collective_iconifiedcategory
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestCategorizedChildView(BaseTestCase):

    def test__call__(self):
        view = self.portal.restrictedTraverse('@@categorized-childs')

        # the category and elements of category is displayed
        result = view()
        self.assertTrue('<img src="http://nohost/plone/config/group-1/category-1-1/@@download/icon/icon1.png"'
                        in result)
        self.assertTrue('<a href="http://nohost/plone/file/@@download/file/file.txt">' in result)
        self.assertTrue('<span title="File description">file.txt</span>' in result)
        self.assertTrue('<a href="http://nohost/plone/image/@@download/file/icon1.png">' in result)
        self.assertTrue('<span title="Image description">icon1.png</span>' in result)

        # in case a file is too large, a warning is displayed
        # manipulate stored categorized_elements
        self.portal.categorized_elements[self.portal['file'].UID()]['warn_filesize'] = True
        self.portal.categorized_elements[self.portal['file'].UID()]['filesize'] = 7000000
        self.assertTrue("(<span class=\'warn_filesize\' title=\'Annex size is huge, "
                        "it could be difficult to be downloaded!\'>6.7 MB</span>)" in view())

        # remove the categorized elements
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        result = lxml.html.fromstring(view())
        self.assertEqual(result.text, 'Nothing.')


class TestCanViewAwareDownload(BaseTestCase):

    def test_default(self):
        # by default @@download returns the file, here
        # it is also the case as IIconifiedContent.can_view adapter returns True by default
        file_obj = self.portal['file']
        img_obj = self.portal['image']
        self.assertTrue(isinstance(file_obj.restrictedTraverse('@@download')(), file))
        self.assertTrue(isinstance(file_obj.restrictedTraverse('@@display-file')(), file))
        self.assertTrue(isinstance(img_obj.restrictedTraverse('@@download')(), file))
        self.assertTrue(isinstance(img_obj.restrictedTraverse('@@display-file')(), file))

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
