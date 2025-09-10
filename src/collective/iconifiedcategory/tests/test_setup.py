# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.iconifiedcategory.testing import COLLECTIVE_ICONIFIED_CATEGORY_INTEGRATION_TESTING
from plone.base.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.iconifiedcategory is properly installed."""

    layer = COLLECTIVE_ICONIFIED_CATEGORY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.installer = get_installer(self.portal, self.request)

    def test_product_installed(self):
        """Test if collective.iconifiedcategory is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'collective.iconifiedcategory'))

    def test_browserlayer(self):
        """Test that ICollectiveIconifiedCategoryLayer is registered."""
        from collective.iconifiedcategory.interfaces import ICollectiveIconifiedCategoryLayer
        from plone.browserlayer import utils
        self.assertIn(ICollectiveIconifiedCategoryLayer,
                      utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_ICONIFIED_CATEGORY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.installer = get_installer(self.portal, self.request)
        self.installer.uninstall_product('collective.iconifiedcategory')

    def test_product_uninstalled(self):
        """Test if collective.iconifiedcategory is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'collective.iconifiedcategory'))
