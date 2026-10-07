# -*- coding: utf-8 -*-

from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from z3c.form import validator


class TestContent(BaseTestCase):

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

    def test_content_view(self):
        category_group = self.portal.config.get('group-1')
        category = category_group.get('category-1-1')
        subcategory = category.get('subcategory-1-1-1')

        # just call the view for every contents
        self.assertTrue(category_group.restrictedTraverse('@@view')())
        self.assertTrue(category.restrictedTraverse('@@view')())
        self.assertTrue(subcategory.restrictedTraverse('@@view')())

    def test_allowed_content_types(self):
        """Only the configuration may be added anywhere, then group > category > subcategory."""
        config = self.portal.config
        group = config['group-1']
        category = group['category-1-1']
        allowed = [t.getId() for t in self.portal.allowedContentTypes()]
        self.assertIn('ContentCategoryConfiguration', allowed)
        self.assertNotIn('ContentCategoryGroup', allowed)
        self.assertNotIn('ContentCategory', allowed)
        self.assertNotIn('ContentSubcategory', allowed)
        self.assertEqual([t.getId() for t in config.allowedContentTypes()], ['ContentCategoryGroup'])
        self.assertEqual([t.getId() for t in group.allowedContentTypes()], ['ContentCategory'])
        self.assertEqual([t.getId() for t in category.allowedContentTypes()], ['ContentSubcategory'])
        self.assertRaises(InvalidParameterError, api.content.create,
                          type='ContentCategory', title='Wrong', icon=self.icon, container=self.portal)
        self.assertRaises(InvalidParameterError, api.content.create,
                          type='ContentSubcategory', title='Wrong', container=group)
        self.assertRaises(InvalidParameterError, api.content.create,
                          type='Document', title='Wrong', container=config)


class TestCategorize(BaseTestCase):
    """ICategorize invariants, checked by the category/subcategory add and edit forms."""

    def _validate(self, **kwargs):
        data = {'to_sign': False, 'signed': False, 'to_approve': False, 'approved': False}
        data.update(kwargs)
        invariants = validator.InvariantsValidator(None, None, None, ICategory, None)
        return [error.args[0] for error in invariants.validate(data)]

    def test_signedInvariant(self):
        msg = u"'Signed' can not be True when 'To sign?' is False!"
        self.assertEqual(self._validate(), [])
        self.assertEqual(self._validate(to_sign=True), [])
        self.assertEqual(self._validate(to_sign=True, signed=True), [])
        self.assertEqual(self._validate(signed=True), [msg])

    def test_approvedInvariant(self):
        msg = u"'Approved' can not be True when 'To approve?' is False!"
        self.assertEqual(self._validate(to_approve=True), [])
        self.assertEqual(self._validate(to_approve=True, approved=True), [])
        self.assertEqual(self._validate(approved=True), [msg])
        self.assertEqual(
            self._validate(signed=True, approved=True),
            [u"'Signed' can not be True when 'To sign?' is False!", msg])
