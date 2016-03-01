# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.categorize.testing import COLLECTIVE_CATEGORIZE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.categorize is properly installed."""

    layer = COLLECTIVE_CATEGORIZE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.categorize is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.categorize'))

    def test_browserlayer(self):
        """Test that ICollectiveCategorizeLayer is registered."""
        from collective.categorize.interfaces import (
            ICollectiveCategorizeLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveCategorizeLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_CATEGORIZE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.categorize'])

    def test_product_uninstalled(self):
        """Test if collective.categorize is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.categorize'))
