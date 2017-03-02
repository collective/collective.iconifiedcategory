# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Products.Five import BrowserView
from collections import OrderedDict
from plone import api
from plone.namedfile.browser import DisplayFile
from plone.namedfile.browser import Download
from zope.component import getMultiAdapter

from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.utils import get_categorized_elements
from collective.iconifiedcategory.utils import render_filesize


class CategorizedChildView(BrowserView):
    """ """
    def __init__(self, context, request):
        """ """
        super(CategorizedChildView, self).__init__(context, request)
        self.portal_url = api.portal.get().absolute_url()

    def update(self):
        self.categorized_elements = get_categorized_elements(
            self.context,
            portal_type=self.portal_type,
        )

    def __call__(self, portal_type=None, show_nothing=True):
        """ """
        self.portal_type = portal_type
        self.show_nothing = show_nothing
        self.update()
        return super(CategorizedChildView, self).__call__()

    def has_elements_to_show(self):
        return ('categorized_elements' in self.context.__dict__ and
                len(self.categorized_elements) > 0)

    def categories_infos(self):
        infos = [(e['category_uid'], {'id': e['category_id'],
                                      'uid': e['category_uid'],
                                      'title': e['category_title'],
                                      'counts': 0,
                                      'icon': e['icon_url']})
                 for e in self.categorized_elements]
        infos = OrderedDict(infos)
        for key, element in infos.items():
            element['counts'] = len([e for e in self.categorized_elements
                                     if e['category_uid'] == key])
        return infos.values()


class CategorizedChildInfosView(BrowserView):
    """ """
    def __init__(self, context, request):
        """ """
        super(CategorizedChildInfosView, self).__init__(context, request)
        self.portal_url = api.portal.get().absolute_url()

    def update(self):
        uids = self._find_uids()
        self.categorized_elements = get_categorized_elements(self.context,
                                                             uids=uids)

    def _find_uids(self):
        """ """
        uids = []
        for k, v in getattr(self.context, 'categorized_elements', {}).items():
            if v['category_uid'] == self.category_uid:
                uids.append(k)
        return uids

    def __call__(self, category_uid):
        """ """
        self.category_uid = category_uid
        self.update()
        return super(CategorizedChildInfosView, self).__call__()

    def show_preview_link(self):
        """Made to be overrided."""
        return True

    @property
    def categories_uids(self):
        return OrderedDict.fromkeys(
            [e['category_uid'] for e in self.categorized_elements],
        ).keys()

    def infos(self):
        infos = OrderedDict([(e, []) for e in self.categories_uids])
        for element in self.categorized_elements:
            infos[element['category_uid']].append(element)
        return infos

    def render_filesize(self, size):
        """ """
        return render_filesize(size)

    def categorized_elements_more_infos_url(self):
        """ """
        return "{0}/{1}".format(self.context.absolute_url(), "@@iconifiedcategory")

    def number_of_columns(self, elements):
        """Return a number to """
        columns_treshold = api.portal.get_registry_record(
            'categorized_childs_infos_columns_threshold',
            interface=IIconifiedCategorySettings,
        )
        columns_treshold = float(columns_treshold)
        return round(len(elements) / columns_treshold)


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
