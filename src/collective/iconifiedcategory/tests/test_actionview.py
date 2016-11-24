# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Products.CMFCore.permissions import ModifyPortalContent
from z3c.json.interfaces import IJSONReader
from zope.component import getUtility

from plone import api
from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.documentviewer.settings import GlobalSettings
from collective.iconifiedcategory.browser.actionview import BaseView
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestBaseView(BaseTestCase):

    def test__call__(self):
        obj = self.portal['file']
        view = BaseView(obj, self.portal.REQUEST)
        reader = getUtility(IJSONReader)

        # when attribute_mapping is not set, it does not work
        result = reader.read(view())
        self.assertEqual(result[u'status'], 1)
        self.assertEqual(result[u'msg'], u'No values to set')

        # only doable if user has Modify portal content on obj
        view.attribute_mapping = {'title': 'action-value-title'}
        self.portal.REQUEST.set('action-value-title', 'My new title')
        obj.manage_permission(ModifyPortalContent, roles=[])
        result = reader.read(view())
        self.assertEqual(result[u'status'], 1)
        self.assertEqual(result[u'msg'], u'Error during process')
        obj.manage_permission(ModifyPortalContent, roles=['Manager'])

        # change title
        self.assertEqual(obj.title, u'file.txt')
        result = reader.read(view())
        self.assertEqual(result[u'status'], 0)
        self.assertEqual(result[u'msg'], u'Values have been set')
        self.assertEqual(obj.title, 'My new title')

    def test_get_current_values(self):
        obj = self.portal['file']
        view = BaseView(obj, self.portal.REQUEST)

        self.assertEqual(view.get_current_values(), {})
        view.attribute_mapping = {'title': 'action-value-title'}
        self.assertEqual(view.get_current_values(), {'title': u'file.txt'})


class TestToPrintChangeView(BaseTestCase):

    def test_set_values(self):
        obj = self.portal['file']
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
        self.assertFalse(obj.to_print)
        view.set_values({'to_print': True})
        self.assertIsNone(obj.to_print)

        # will be correctly set if format is managed
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        view.set_values({'to_print': True})
        self.assertTrue(obj.to_print)
        view.set_values({'to_print': False})
        self.assertFalse(obj.to_print)


class TestConfidentialChangeView(BaseTestCase):

    def test_set_values(self):
        obj = self.portal['file']
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
        self.assertTrue(obj.confidential)
        view.set_values({'confidential': False})
        self.assertFalse(obj.confidential)
