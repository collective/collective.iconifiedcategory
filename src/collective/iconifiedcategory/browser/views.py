# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from collections import OrderedDict
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.utils import confidential_message
from collective.iconifiedcategory.utils import get_categorized_elements
from collective.iconifiedcategory.utils import print_message
from collective.iconifiedcategory.utils import render_filesize
from collective.iconifiedcategory.utils import signed_message
from DateTime import DateTime
from plone import api
from plone.formwidget.namedfile.widget import Download as fnw_Download
from plone.namedfile.browser import DisplayFile
from plone.namedfile.browser import Download
from plone.namedfile.scaling import ImageScaling
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.Five import BrowserView
from zope.component import getMultiAdapter


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
        self.have_details_to_show = False

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
        """Return number of columns to display categorized_elements on
           when displaying many elements."""
        columns_treshold = api.portal.get_registry_record(
            'categorized_childs_infos_columns_threshold',
            interface=IIconifiedCategorySettings,
        )
        columns_treshold = float(columns_treshold)
        return round(len(elements) / columns_treshold)

    def show_to_print(self, element):
        """ """
        show = element['to_be_printed_activated']
        if show:
            self.have_details_to_show = True
        return show

    def show_confidential(self, element):
        """ """
        show = element['confidentiality_activated']
        if show:
            self.have_details_to_show = True
        return show

    def show_signed(self, element):
        """ """
        show = element['signed_activated']
        if show:
            self.have_details_to_show = True
        return show

    def show_details_action(self):
        """ """
        return self.have_details_to_show

    def get_css_classses_for(self, functionnality, element):
        """ """
        css_classes = []
        if functionnality == "to_print":
            css_classes.append("iconified-print")
            if element['to_print'] is None:
                css_classes.append('deactivated')
            elif element['to_print'] is True:
                css_classes.append('active')
        elif functionnality == "confidential":
            css_classes.append("iconified-confidential")
            if element['confidential'] is True:
                css_classes.append('active')
        elif functionnality == "signed":
            css_classes.append("iconified-signed")
            if element['to_sign'] is False:
                css_classes.append('deactivated')
            elif element['signed'] is True:
                css_classes.append('active')
        return " ".join(css_classes)

    def get_tag_title_for(self, functionnality, element):
        """ """
        msg = ''
        if functionnality == "to_print":
            msg = print_message(to_print_value=element['to_print'])
        elif functionnality == "confidential":
            msg = confidential_message(confidential_value=element['confidential'])
        elif functionnality == "signed":
            msg = signed_message(to_sign_value=element['to_sign'],
                                 signed_value=element['signed'])
        return msg


def check_can_view(obj, request):
    """ """
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(UID=obj.UID())
    brain = brains[0]
    adapter = getMultiAdapter((obj.aq_parent, request, brain),
                              IIconifiedContent)
    return adapter.can_view()


class CanViewAwareDownload(Download):
    """ """
    def __call__(self):
        if not check_can_view(self.context, self.request):
            raise Unauthorized
        return super(CanViewAwareDownload, self).__call__()


class CanViewAwareDisplayFile(DisplayFile, CanViewAwareDownload):
    """ """


class CanViewAwareFNWDownload(fnw_Download):
    """ """
    def __call__(self):
        if not check_can_view(aq_inner(self.context.context), self.request):
            raise Unauthorized
        return super(CanViewAwareFNWDownload, self).__call__()


class ImageDataModifiedImageScaling(ImageScaling):
    """ """

    def modified(self):
        """Returns the stored file _p_mtime instead content _p_mtime."""
        context = aq_base(self.context)
        value = IPrimaryFieldInfo(context).value
        date = DateTime(value._p_mtime)
        return date.millis()
