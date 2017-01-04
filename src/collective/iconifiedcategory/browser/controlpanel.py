# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.app.registry.browser import controlpanel

from collective.iconifiedcategory import _
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings


class IconifiedCategorySettingsEditForm(controlpanel.RegistryEditForm):
    schema = IIconifiedCategorySettings
    label = _(u'Iconified Category Settings')


class IconifiedCategorySettingsView(controlpanel.ControlPanelFormWrapper):
    form = IconifiedCategorySettingsEditForm
