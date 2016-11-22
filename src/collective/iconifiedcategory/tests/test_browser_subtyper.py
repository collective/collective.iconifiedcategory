# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory.tests.base import BaseTestCase


class TestIconifiedCategorySubtyper(BaseTestCase):

    def _subtyper(self, obj, prop):
        subtyper = obj.restrictedTraverse('@@iconified_subtyper')
        return getattr(subtyper, prop)

    def test_have_categorized_elements(self):
        """Test the have_categorized_elements property"""
        self.assertTrue(self._subtyper(
            self.portal,
            'have_categorized_elements',
        ))
        self.assertFalse(self._subtyper(
            self.portal['config'],
            'have_categorized_elements',
        ))

    def test_on_config(self):
        """Test the on_config property"""
        self.assertFalse(self._subtyper(self.portal, 'on_config'))
        self.assertTrue(self._subtyper(self.portal['config'], 'on_config'))
        self.assertTrue(self._subtyper(
            self.portal['config']['group-1'],
            'on_config',
        ))
        self.assertTrue(self._subtyper(
            self.portal['config']['group-1']['category-1-1'],
            'on_config',
        ))
        self.assertTrue(self._subtyper(
            self.portal['config']['group-1']['category-1-1']['subcategory-1-1-1'],
            'on_config',
        ))
