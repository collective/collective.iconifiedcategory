# -*- coding: utf-8 -*-

from collective.iconifiedcategory import testing
from collective.iconifiedcategory.utils import _modified
from plone import api
from plone import namedfile
from plone.app.testing import login
from zope.component import getGlobalSiteManager

import os
import unittest


class BaseTestCase(unittest.TestCase):

    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    @property
    def image(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, "icône1.png"), "rb")
        return namedfile.NamedBlobFile(f.read(), filename="icône1.png")

    @property
    def file(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, "file.txt"), "rb")
        return namedfile.NamedBlobFile(f.read(), filename="file.txt")

    @property
    def file_pdf(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, "file.pdf"), "rb")
        return namedfile.NamedBlobFile(f.read(), filename="file.pdf")

    @property
    def icon(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, "icône1.png"), "rb")
        return namedfile.NamedBlobFile(f.read(), filename="icône1.png")

    def _modified(self, obj):
        return _modified(obj)

    def register_adapter(self, factory, required, provided):
        """Register a global adapter for the current test only."""
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory, required, provided)
        self.addCleanup(gsm.unregisterAdapter, factory, required, provided)

    def setUp(self):
        self.maxDiff = None
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.config = self.portal["config"]
        api.user.create(
            email="test@test.com",
            username="adminuser",
            password="secret12",
        )
        api.user.grant_roles(
            username="adminuser",
            roles=["Manager"],
        )
        login(self.portal, "adminuser")
        api.content.create(
            id="file_txt",
            type="File",
            file=self.file,
            container=self.portal,
            description="File description",
            content_category="config_-_group-1_-_category-1-1",
            to_print=False,
            confidential=False,
            publishable=False,
        )
        cat_id = "config_-_group-1_-_category-1-1_-_subcategory-1-1-1"
        api.content.create(
            id="image",
            type="Image",
            image=self.image,
            container=self.portal,
            description="Image description",
            content_category=cat_id,
            to_print=False,
            confidential=False,
            publishable=False,
        )

    def tearDown(self):
        login(self.portal, "adminuser")
        elements = ("file_txt", "image")
        for element in elements:
            if element in self.portal:
                api.content.delete(self.portal[element])
