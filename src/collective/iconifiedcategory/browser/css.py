# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import utils
from plone import api
from plone.memoize import ram
from Products.Five import BrowserView


css_pattern = (
    ".{0} {{ padding-left: 1.4em; background: "
    "transparent url('{1}') no-repeat top left; "
    "background-size: contain; }}"
)


def _categories_css_cachekey(method, portal):
    """Every category change reindexes the catalog; urls depend on the virtual host."""
    return portal.absolute_url(), api.portal.get_tool("portal_catalog").getCounter()


@ram.cache(_categories_css_cachekey)
def categories_css(portal):
    """One rule per category: its icon in front of the elements having its css class."""
    if utils.has_config_root(portal) is False:
        return ""
    content = []
    # sort_on=None to avoid useless sort_on="getObjPositionInParent"
    for category in utils.get_categories(portal, sort_on=None, only_enabled=False):
        obj = category._unrestrictedGetObject()
        category_id = utils.calculate_category_id(obj)
        url = "{0}/@@download".format(obj.absolute_url())
        content.append(css_pattern.format(utils.format_id_css(category_id), url))
    return "\n".join(content)


class IconifiedCategory(BrowserView):
    """@@collective-iconifiedcategory.css, served by the iconifiedcategory-dynamic bundle:
    Plone renders its url with a hash of its content, so a category change busts the browser cache.
    """

    def __call__(self):
        self.request.response.setHeader("Content-Type", "text/css")
        return categories_css(api.portal.get())
