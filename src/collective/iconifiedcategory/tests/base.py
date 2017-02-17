# -*- coding: utf-8 -*-

import os
import unittest

from plone import api
from plone import namedfile
from plone.app.testing import login

from collective.iconifiedcategory import testing


class BaseTestCase(unittest.TestCase):

    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    @property
    def image(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'icône1.png'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'icône1.png')

    @property
    def file(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'file.txt'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'file.txt')

    @property
    def icon(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'icône1.png'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'icône1.png')

    def setUp(self):
        self.maxDiff = None
        self.portal = self.layer['portal']
        self.config = self.portal['config']
        api.user.create(
            email='test@test.com',
            username='adminuser',
            password='secret',
        )
        api.user.grant_roles(
            username='adminuser',
            roles=['Manager'],
        )
        login(self.portal, 'adminuser')
        api.content.create(
            id='file',
            type='File',
            file=self.file,
            container=self.portal,
            description='File description',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        cat_id = 'config_-_group-1_-_category-1-1_-_subcategory-1-1-1'
        api.content.create(
            id='image',
            type='Image',
            image=self.image,
            container=self.portal,
            description='Image description',
            content_category=cat_id,
            to_print=False,
            confidential=False,
        )

    def tearDown(self):
        elements = ('file', 'image')
        for element in elements:
            if element in self.portal:
                api.content.delete(self.portal[element])
