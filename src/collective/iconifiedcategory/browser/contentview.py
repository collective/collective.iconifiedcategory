# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory.content.categorygroup import ICategoryGroup
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from zope.interface import classImplements


class FormMixin(object):
    related_widgets = {
        'confidential': 'confidentiality_activated',
        'to_print': 'to_be_printed_activated',
        'to_sign': 'signed_activated',
        'signed': 'signed_activated',
    }

    @property
    def category_group(self):
        if ICategoryGroup.providedBy(self.context):
            return self.context
        return self.context.get_category_group()

    def updateWidgets(self):
        super(FormMixin, self).updateWidgets()
        for name, widget in self.widgets.items():
            related_attribute = self.related_widgets.get(name)
            if not related_attribute:
                continue
            if getattr(self.category_group, related_attribute) is False:
                widget.mode = HIDDEN_MODE


class BaseEditForm(FormMixin, DefaultEditForm):
    pass


BaseEditView = layout.wrap_form(BaseEditForm)
classImplements(BaseEditView, IDexterityEditForm)


class BaseAddForm(FormMixin, DefaultAddForm):
    pass


class BaseAddView(DefaultAddView):
    form = BaseAddForm


class BaseView(DefaultView):
    related_widgets = {
        'confidential': 'confidentiality_activated',
        'to_print': 'to_be_printed_activated',
        'to_sign': 'signed_activated',
        'signed': 'signed_activated',
    }

    def updateWidgets(self):
        super(BaseView, self).updateWidgets()
        for rel_widget, rel_attribute in self.related_widgets.items():
            parent_value = getattr(
                self.context.get_category_group(),
                rel_attribute,
                None,
            )
            if parent_value is False and rel_widget in self.widgets:
                del self.widgets[rel_widget]
