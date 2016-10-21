# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase


class TestEditView(BaseTestCase):

    def test_edit_form(self):
        category_group = self.portal.config.get('group-1')
        category = category_group.get('category-1-1')
        subcategory = category.get('subcategory-1-1-1')

        # edit form is overrided for 'ContentCategory'
        self.assertEqual(category.portal_type, 'ContentCategory')
        edit = category.restrictedTraverse('@@edit')
        self.assertEqual(edit.context.get_category_group(), category_group)
        self.assertTrue(category.restrictedTraverse('@@edit')())

        # edit form is overrided for 'ContentSubcategory'
        self.assertEqual(subcategory.portal_type, 'ContentSubcategory')
        edit = subcategory.restrictedTraverse('@@edit')
        self.assertEqual(edit.context.get_category_group(), category_group)
        self.assertTrue(subcategory.restrictedTraverse('@@edit')())
