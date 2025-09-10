# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import utils
# from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from datetime import datetime, timezone
from plone.app.theming.browser.custom_css import CustomCSSView
from plone.app.theming.interfaces import IThemeSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class IconifiedCategory(CustomCSSView):

    def __call__(self, *args, **kwargs):
        self.request.response.setHeader('Content-Type', 'text/css')
        base_css = super().__call__()
        dynamic_css = self._dynamic_css()
        lm = self._last_modified()
        if lm:
            self.request.response.setHeader(
                "Last-Modified",
                lm.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            )
        return "\n".join([c for c in (base_css, dynamic_css) if c])

    def _dynamic_css(self):
        content = []
        css = (u".{0} {{ padding-left: 2em; background: "
               u"transparent url('{1}') no-repeat top left; "
               u"background-size: contain; }}")
        if utils.has_config_root(self.context) is False:
            return ''
        # sort_on=None to avoid useless sort_on="getObjPositionInParent"
        categories = utils.get_categories(self.context,
                                          sort_on=None,
                                          only_enabled=False)
        for category in categories:
            obj = category._unrestrictedGetObject()
            category_id = utils.calculate_category_id(obj)
            url = u'{0}/@@download'.format(obj.absolute_url())
            content.append(css.format(utils.format_id_css(category_id), url))
        return ' '.join(content)

    def _last_modified(self):
        registry = getUtility(IRegistry)
        lm_list = []
        theme_settings = registry.forInterface(IThemeSettings, False)
        lm_list.append(theme_settings.custom_css_timestamp)
        # iconified = registry.forInterface(IIconifiedCategorySettings)
        # lm_list.append(iconified.css_timestamp)
        lm_list = [d for d in lm_list if d]
        if lm_list:
            return max(lm_list)
        return datetime.now(timezone.utc)
