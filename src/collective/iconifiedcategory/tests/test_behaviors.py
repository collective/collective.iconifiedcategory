# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.documentviewer.settings import GlobalSettings
from collective.iconifiedcategory import testing
from collective.iconifiedcategory.behaviors.iconifiedcategorization import IIconifiedCategorization
from collective.iconifiedcategory.tests.base import BaseTestCase
from collective.iconifiedcategory.utils import calculate_category_id
from collective.iconifiedcategory.utils import get_category_object
from plone import api
from z3c.form import validator
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from ZPublisher.HTTPRequest import FileUpload

import cgi
import unittest


class TestIconifiedCategorization(BaseTestCase, unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def test_content_category_edit_form(self):
        """ """
        # displayed on the edit form
        edit = self.portal.file_txt.restrictedTraverse('@@edit')
        edit.update()
        rendered_edit = edit()
        self.assertTrue('IIconifiedCategorization.content_category' in rendered_edit)
        self.assertTrue('IIconifiedCategorization.default_titles' in rendered_edit)

    def test_content_category_not_set_if_not_activated(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.to_be_printed_activated = False
        category_group.confidentiality_activated = False
        category.to_print = True
        category.confidential = True
        obj = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(obj.to_print)
        self.assertFalse(obj.confidential)

    def test_content_category_confidential_on_creation(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.confidentiality_activated = True

        # set to False
        category.confidential = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(file2.confidential)

        # set to True
        category.confidential = True
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file3.confidential)

    def test_content_category_to_print_on_creation(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.to_be_printed_activated = True
        # enable conversion
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()

        # set to False
        category.to_print = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(file2.to_print)

        # set to True
        category.to_print = True
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file3.to_print)

    def test_content_category_to_sign_signed_on_creation(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.signed_activated = True

        # set to False both attributes
        category.to_sign = False
        category.signed = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(file2.to_sign)
        self.assertFalse(file2.signed)

        # set True for to_sign, False for signed
        category.to_sign = True
        category.signed = False
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file3.to_sign)
        self.assertFalse(file3.signed)

        # set True for both attributes
        category.to_sign = True
        category.signed = True
        file4 = api.content.create(
            id='file4',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file4.to_sign)
        self.assertTrue(file4.signed)

    def test_content_category_to_print_only_set_if_convertible_when_conversion_enabled(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.to_be_printed_activated = True

        # set to True
        category.to_print = True
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        # enable conversion
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        file2.file.contentType = 'text/unknown'

        notify(ObjectModifiedEvent(file2))
        self.assertIsNone(file2.to_print)

    def test_content_category_setter_reindex_content_category_uid(self):
        """ """
        catalog = api.portal.get_tool('portal_catalog')
        obj = self.portal['file_txt']
        category = get_category_object(obj, obj.content_category)
        # correctly indexed on creation
        category_brain = catalog(content_category_uid=category.UID())[0]
        self.assertEqual(category_brain.UID, obj.UID())
        obj_brain = catalog(UID=obj.UID())[0]
        self.assertEqual(obj_brain.content_category_uid, category.UID())
        # correctly reindexed when content_category changed thru setter
        category2 = self.portal.config['group-1']['category-1-2']
        self.assertNotEqual(category, category2)
        adapted_obj = IIconifiedCategorization(obj)
        setattr(adapted_obj, 'content_category', 'config_-_group-1_-_category-1-2')
        category2_brain = catalog(content_category_uid=category2.UID())[0]
        self.assertEqual(category2_brain.UID, obj.UID())
        obj_brain = catalog(UID=obj.UID())[0]
        self.assertEqual(obj_brain.content_category_uid, category2.UID())

    def test_content_category_changed_default_values(self):
        """While content_category is changed on an element, the default values for fields
           to_print/confidential/to_sign/signed are reapplied with new content_category
           default values if it was still the default value of the original content_category."""
        category_group = self.portal.config['group-1']
        category_group.to_be_printed_activated = True
        category_group.confidentiality_activated = True
        category_group.signed_activated = True
        category11 = self.portal.config['group-1']['category-1-1']
        category11_id = calculate_category_id(category11)
        obj = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=category11_id)
        self.assertFalse(obj.confidential)
        self.assertFalse(obj.to_sign)
        self.assertFalse(obj.signed)
        self.assertIsNone(obj.to_print)
        # now enable everything on category-1-2 and use it
        category12 = self.portal.config['group-1']['category-1-2']
        category12.to_print = False
        category12.confidential = True
        category12.to_sign = True
        category12.signed = True
        category12_id = calculate_category_id(category12)
        adapted_obj = IIconifiedCategorization(obj)
        setattr(adapted_obj, 'content_category', category12_id)
        notify(ObjectModifiedEvent(obj))

        # changed to True on obj an in parent's categorized_elements
        parent_cat_elements = obj.aq_parent.categorized_elements[obj.UID()]
        self.assertTrue(obj.confidential)
        self.assertTrue(parent_cat_elements['confidential'])
        self.assertTrue(obj.to_sign)
        self.assertTrue(parent_cat_elements['to_sign'])
        self.assertTrue(obj.signed)
        self.assertTrue(parent_cat_elements['signed'])
        # to_print could not be set to False because not printable
        self.assertIsNone(obj.to_print)
        self.assertIsNone(parent_cat_elements['to_print'])

        # enable conversion and back to category11
        category11.to_print = True
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        # set to_print to False, aka the default value of category12
        obj.to_print = False
        setattr(adapted_obj, 'content_category', category11_id)
        notify(ObjectModifiedEvent(obj))
        self.assertTrue(obj.to_print)
        self.assertTrue(parent_cat_elements['to_print'])

        # if original content_category does not exist, it does not fail
        # but default values are not reapplied
        obj.content_category = 'unkown_content_category'
        setattr(adapted_obj, 'content_category', category12_id)
        notify(ObjectModifiedEvent(obj))
        self.assertEqual(obj.content_category, category12_id)

    def test_unexisting_content_category(self):
        """Storing an unexisting content_category does not break anything."""
        obj = api.content.create(
            id='my-file',
            type='File',
            file=self.file,
            container=self.portal,
            content_category='unexisting_content_category_uid')
        self.assertTrue(obj)

    def test_only_pdf_invariant(self):
        """When category.only_pdf is True, categorized file may only be a PDF file."""
        category = self.portal.config['group-1']['category-1-1']
        category.only_pdf = False
        content_category_id = calculate_category_id(category)
        invariants = validator.InvariantsValidator(
            None, None, None, IIconifiedCategorization, None)
        # form and data in request
        fieldstorage = cgi.FieldStorage()
        fieldstorage.file = self.file.data
        fieldstorage.filename = self.file.filename
        data = {}
        data['content_category'] = content_category_id
        request = self.portal.REQUEST
        request.form['form.widgets.file'] = FileUpload(fieldstorage)
        view = self.portal.restrictedTraverse('folder_contents')
        request['PUBLISHED'] = view
        self.assertFalse(invariants.validate(data))
        # already_validateFileIsPDF was set in REQUEST
        self.assertTrue(request.get('already_validateFileIsPDF'))
        self.assertFalse(invariants.validate(data))
        # PDF needed
        request.set('already_validateFileIsPDF', False)
        category.only_pdf = True
        errors = invariants.validate(data)
        request.set('already_validateFileIsPDF', False)
        self.assertEqual(errors[0].message, u'You must select a PDF file!')
        request.form['form.widgets.file'].headers['content-type'] = 'application/pdf'
        # no file in request
        request.form = {}
        self.assertFalse(invariants.validate(data))
        request.set('already_validateFileIsPDF', False)
        # editing a stored element
        category.only_pdf = False
        obj = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        view = obj.restrictedTraverse('view')
        request['PUBLISHED'] = view
        self.assertFalse(invariants.validate(data))
        request.set('already_validateFileIsPDF', False)
        # PDF needed
        category.only_pdf = True
        errors = invariants.validate(data)
        request.set('already_validateFileIsPDF', False)
        self.assertEqual(errors[0].message, u'You must select a PDF file!')
        obj.file = self.file_pdf
        self.assertFalse(invariants.validate(data))
