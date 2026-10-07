# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase


FLAG_FIELDS = ('confidential', 'to_print', 'to_sign', 'signed', 'to_approve', 'approved', 'publishable')


class ContentViewTestCase(BaseTestCase):

    def setUp(self):
        super(ContentViewTestCase, self).setUp()
        # testing profile: only to_be_printed_activated is True on the groups
        self.group = self.config['group-1']
        self.category = self.group['category-1-1']
        self.subcategory = self.category['subcategory-1-1-1']

    def _activate_every_option(self):
        self.group.confidentiality_activated = True
        self.group.signed_activated = True
        self.group.approved_activated = True
        self.group.publishable_activated = True


class TestFormMixin(ContentViewTestCase):

    def _forms(self):
        """Add and edit forms of categories and subcategories, rendered."""
        views = (
            self.group.restrictedTraverse('++add++ContentCategory'),
            self.category.restrictedTraverse('++add++ContentSubcategory'),
            self.category.restrictedTraverse('@@edit'),
            self.subcategory.restrictedTraverse('@@edit'),
        )
        for view in views:
            view()
        return [view.form_instance for view in views]

    def _modes(self, form):
        return dict([(name, form.widgets[name].mode) for name in FLAG_FIELDS])

    def test_category_group(self):
        self.assertEqual([form.category_group for form in self._forms()], [self.group] * 4)

    def test_updateWidgets(self):
        # publishable is never hidden, it is not in related_widgets
        expected = {'confidential': 'hidden', 'to_print': 'input', 'to_sign': 'hidden', 'signed': 'hidden',
                    'to_approve': 'hidden', 'approved': 'hidden', 'publishable': 'input'}
        for form in self._forms():
            self.assertEqual(self._modes(form), expected)
        self._activate_every_option()
        for form in self._forms():
            self.assertEqual(self._modes(form), dict([(name, 'input') for name in FLAG_FIELDS]))


class TestBaseView(ContentViewTestCase):

    def _displayed(self, obj):
        view = obj.restrictedTraverse('@@view')
        view()
        return [name for name in FLAG_FIELDS if name in view.widgets]

    def test_updateWidgets(self):
        # publishable is never removed, it is not in related_widgets
        self.assertEqual(self._displayed(self.category), ['to_print', 'publishable'])
        self.assertEqual(self._displayed(self.subcategory), ['to_print', 'publishable'])
        self._activate_every_option()
        self.assertEqual(self._displayed(self.category), list(FLAG_FIELDS))
        self.assertEqual(self._displayed(self.subcategory), list(FLAG_FIELDS))
