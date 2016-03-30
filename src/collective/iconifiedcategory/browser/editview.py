# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from zope.interface import classImplements

from collective.iconifiedcategory.content.categorygroup import ICategoryGroup


class BaseEditForm(DefaultEditForm):
    related_widgets = {
        'confidential': 'confidentiality_activated',
        'to_print': 'to_be_printed_activated',
    }

    def updateWidgets(self):
        super(BaseEditForm, self).updateWidgets()
        for name, widget in self.widgets.items():
            related_attribute = self.related_widgets.get(name)
            if not related_attribute:
                continue
            if getattr(self.category_group, related_attribute) is False:
                widget.mode = HIDDEN_MODE

    @property
    def category_group(self):
        parent = self.context.aq_parent
        while ICategoryGroup.providedBy(parent) is False:
            parent = parent.aq_parent
        return parent


BaseEditView = layout.wrap_form(BaseEditForm)
classImplements(BaseEditView, IDexterityEditForm)
