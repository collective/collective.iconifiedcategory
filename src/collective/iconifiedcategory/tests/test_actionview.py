# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.documentviewer.settings import GlobalSettings
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.browser.actionview import BaseView
from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from Products.CMFCore.permissions import ModifyPortalContent
from z3c.json.interfaces import IJSONReader
from zope.component import getUtility


class TestBaseView(BaseTestCase):

    def test__call__(self):
        obj = self.portal['file_txt']
        view = BaseView(obj, self.portal.REQUEST)
        reader = getUtility(IJSONReader)

        # when attribute_mapping is not set, it does not work
        result = reader.read(view())
        self.assertEqual(result[u'status'], 2)
        self.assertEqual(result[u'msg'], u'No values to set')

        # only doable if user has Modify portal content on obj
        view.attribute_mapping = {'title': 'action-value-title'}
        self.portal.REQUEST.set('action-value-title', 'My new title')
        obj.manage_permission(ModifyPortalContent, roles=[])
        result = reader.read(view())
        self.assertEqual(result[u'status'], 2)
        self.assertEqual(result[u'msg'], u'Error during process')
        obj.manage_permission(ModifyPortalContent, roles=['Manager'])

        # change title
        self.assertEqual(obj.title, u'file.txt')
        result = reader.read(view())
        self.assertEqual(result[u'status'], -1)
        self.assertEqual(result[u'msg'], u'Values have been set')
        self.assertEqual(obj.title, 'My new title')

    def test_get_current_values(self):
        obj = self.portal['file_txt']
        view = BaseView(obj, self.portal.REQUEST)

        self.assertEqual(view.get_current_values(), {})
        view.attribute_mapping = {'title': 'action-value-title'}
        self.assertEqual(view.get_current_values(), {'title': u'file.txt'})


class TestToPrintChangeView(BaseTestCase):

    def test_set_values(self):
        obj = self.portal['file_txt']
        view = obj.restrictedTraverse('@@iconified-print')

        # works only if functionnality enabled and user have Modify portal content
        category = utils.get_category_object(obj, obj.content_category)
        group = category.get_category_group()

        # fails if one of 2 conditions is not fullfilled
        self.assertTrue(api.user.has_permission(ModifyPortalContent, obj=obj))
        group.to_be_printed_activated = False
        self.assertRaises(Unauthorized, view.set_values, {'to_print': True})
        group.to_be_printed_activated = True

        obj.manage_permission(ModifyPortalContent, roles=[])
        self.assertRaises(Unauthorized, view.set_values, {'to_print': True})
        obj.manage_permission(ModifyPortalContent, roles=['Manager'])

        # set to None when format not managed by collective.documentviewer
        self.assertFalse(obj.to_print, obj.aq_parent.categorized_elements[obj.UID()]['to_print'])
        view.set_values({'to_print': True})
        self.assertIsNone(obj.to_print, obj.aq_parent.categorized_elements[obj.UID()]['to_print'])

        # will be correctly set if format is managed
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        view.set_values({'to_print': True})
        self.assertTrue(obj.to_print, obj.aq_parent.categorized_elements[obj.UID()]['to_print'])
        view.set_values({'to_print': False})
        self.assertFalse(obj.to_print, obj.aq_parent.categorized_elements[obj.UID()]['to_print'])


class TestConfidentialChangeView(BaseTestCase):

    def test_set_values(self):
        obj = self.portal['file_txt']
        view = obj.restrictedTraverse('@@iconified-confidential')

        # works only if functionnality enabled and user have Modify portal content
        category = utils.get_category_object(obj, obj.content_category)
        group = category.get_category_group()

        # fails if one of 2 conditions is not fullfilled
        self.assertTrue(api.user.has_permission(ModifyPortalContent, obj=obj))
        group.confidentiality_activated = False
        self.assertRaises(Unauthorized, view.set_values, {'confidential': True})
        group.confidentiality_activated = True

        obj.manage_permission(ModifyPortalContent, roles=[])
        self.assertRaises(Unauthorized, view.set_values, {'confidential': True})
        obj.manage_permission(ModifyPortalContent, roles=['Manager'])

        # functionnality enabled and user have Modify portal content
        self.assertFalse(obj.confidential)
        view.set_values({'confidential': True})
        self.assertTrue(obj.confidential, obj.aq_parent.categorized_elements[obj.UID()]['confidential'])
        view.set_values({'confidential': False})
        self.assertFalse(obj.confidential, obj.aq_parent.categorized_elements[obj.UID()]['confidential'])


class TestSignedChangeView(BaseTestCase):

    def test_set_values(self):
        obj = self.portal['file_txt']
        view = obj.restrictedTraverse('@@iconified-signed')

        # works only if functionnality enabled and user have Modify portal content
        category = utils.get_category_object(obj, obj.content_category)
        group = category.get_category_group()

        # fails if one of 2 conditions is not fullfilled
        self.assertTrue(api.user.has_permission(ModifyPortalContent, obj=obj))
        group.signed_activated = False
        self.assertRaises(Unauthorized, view.set_values, {'to_sign': True})
        group.signed_activated = True

        obj.manage_permission(ModifyPortalContent, roles=[])
        self.assertRaises(Unauthorized, view.set_values, {'to_sign': True})
        obj.manage_permission(ModifyPortalContent, roles=['Manager'])

        # functionnality enabled and user have Modify portal content
        self.assertFalse(obj.to_sign, obj.aq_parent.categorized_elements[obj.UID()]['to_sign'])
        self.assertFalse(obj.signed, obj.aq_parent.categorized_elements[obj.UID()]['signed'])

        view.set_values({'to_sign': True})
        self.assertTrue(obj.to_sign, obj.aq_parent.categorized_elements[obj.UID()]['to_sign'])
        view.set_values({'signed': True})
        self.assertTrue(obj.signed, obj.aq_parent.categorized_elements[obj.UID()]['signed'])

        # multiple attributes may be set at the same time
        view.set_values({'to_sign': False, 'signed': False})
        self.assertFalse(obj.to_sign, obj.aq_parent.categorized_elements[obj.UID()]['to_sign'])
        self.assertFalse(obj.signed, obj.aq_parent.categorized_elements[obj.UID()]['signed'])
        view.set_values({'to_sign': True, 'signed': False})
        self.assertTrue(obj.to_sign, obj.aq_parent.categorized_elements[obj.UID()]['to_sign'])
        self.assertFalse(obj.signed, obj.aq_parent.categorized_elements[obj.UID()]['signed'])
        view.set_values({'to_sign': True, 'signed': True})
        self.assertTrue(obj.to_sign, obj.aq_parent.categorized_elements[obj.UID()]['to_sign'])
        self.assertTrue(obj.signed, obj.aq_parent.categorized_elements[obj.UID()]['signed'])

    def test_get_next_values(self):
        """to_sign/signed are logically linked and the action in the UI
           will loop among possible values :
           - to_sign False, signed False;
           - to_sign True, signed False,
           - to_sign True, signed True.
           to_sign False, signed True is not possible."""
        obj = self.portal['file_txt']
        view = obj.restrictedTraverse('@@iconified-signed')
        category = utils.get_category_object(obj, obj.content_category)
        group = category.get_category_group()
        group.signed_activated = True
        # loop between possibilities
        self.assertEqual(
            view._get_next_values({'to_sign': False, 'signed': False}),
            (0, {'to_sign': True, 'signed': False}))
        self.assertEqual(
            view._get_next_values({'to_sign': True, 'signed': False}),
            (1, {'to_sign': True, 'signed': True}))
        self.assertEqual(
            view._get_next_values({'to_sign': True, 'signed': True}),
            (-1, {'to_sign': False, 'signed': False}))
        # not possible values, back to 'to_sign'
        self.assertEqual(
            view._get_next_values({'to_sign': False, 'signed': True}),
            (0, {'to_sign': True, 'signed': False}))


class TestPublishableChangeView(BaseTestCase):

    def test_set_values(self):
        obj = self.portal['file_txt']
        view = obj.restrictedTraverse('@@iconified-publishable')

        # works only if functionnality enabled and user have Modify portal content
        category = utils.get_category_object(obj, obj.content_category)
        group = category.get_category_group()

        # fails if one of 2 conditions is not fullfilled
        self.assertTrue(api.user.has_permission(ModifyPortalContent, obj=obj))
        group.publishable_activated = False
        self.assertRaises(Unauthorized, view.set_values, {'publishable': True})
        group.publishable_activated = True

        obj.manage_permission(ModifyPortalContent, roles=[])
        self.assertRaises(Unauthorized, view.set_values, {'publishable': True})
        obj.manage_permission(ModifyPortalContent, roles=['Manager'])

        # functionnality enabled and user have Modify portal content
        self.assertFalse(obj.publishable)
        view.set_values({'publishable': True})
        self.assertTrue(obj.publishable, obj.aq_parent.categorized_elements[obj.UID()]['publishable'])
        view.set_values({'publishable': False})
        self.assertFalse(obj.publishable, obj.aq_parent.categorized_elements[obj.UID()]['publishable'])
