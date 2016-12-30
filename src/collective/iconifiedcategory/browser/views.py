# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Products.Five import BrowserView
from collections import OrderedDict
from plone import api
from plone.namedfile.browser import DisplayFile
from plone.namedfile.browser import Download
from zope.component import getMultiAdapter

from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.utils import get_categorized_elements
from collective.iconifiedcategory.utils import render_filesize


class CategorizedChildView(BrowserView):
    """ """
    def __init__(self, context, request):
        """ """
        super(CategorizedChildView, self).__init__(context, request)
        self.portal_url = api.portal.get().absolute_url()

    def __call__(self, portal_type=None):
        """ """
        self.portal_type = portal_type
        self.categorized_elements = get_categorized_elements(self.context,
                                                             portal_type=portal_type,
                                                             sort_on='category_title')
        return super(CategorizedChildView, self).__call__()

    def can_view(self):
        return ('categorized_elements' in self.context.__dict__ and
                len(self.categorized_elements) > 0)

    def showPreviewLink(self):
        """Made to be overrided."""
        return True

    def categories_infos(self):
        infos = [(e['category_uid'], {'id': e['category_id'],
                                      'title': e['category_title'],
                                      'counts': 0,
                                      'icon': e['icon_url']})
                 for e in self.categorized_elements]
        infos = OrderedDict(sorted(infos, key=lambda x: x[1]['title']))
        for key, element in infos.items():
            element['counts'] = len([e for e in self.categorized_elements
                                     if e['category_uid'] == key])
        return infos.values()

    @property
    def categories_ids(self):
        return set([e['category_id'] for e in self.categorized_elements])

    def infos(self):
        infos = OrderedDict([(e, []) for e in self.categories_ids])
        for element in self.categorized_elements:
            infos[element['category_id']].append(element)
        return infos

    def render_filesize(self, size):
        """ """
        return render_filesize(size)

    def categorized_elements_more_infos_url(self):
        """ """
        return "{0}/{1}".format(self.context.absolute_url(), "@@iconifiedcategory")


class CanViewAwareDownload(Download):
    """ """
    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=self.context.UID())
        brain = brains[0]
        adapter = getMultiAdapter((self.context.aq_parent, self.request, brain),
                                  IIconifiedContent)
        if not adapter.can_view():
            raise Unauthorized
        return super(CanViewAwareDownload, self).__call__()


class CanViewAwareDisplayFile(DisplayFile, CanViewAwareDownload):
    """ """
