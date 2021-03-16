# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import _
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from plone.app.registry.browser import controlpanel


class IconifiedCategorySettingsEditForm(controlpanel.RegistryEditForm):
    schema = IIconifiedCategorySettings
    label = _(u'Iconified Category Settings')


class IconifiedCategorySettingsView(controlpanel.ControlPanelFormWrapper):
    form = IconifiedCategorySettingsEditForm
