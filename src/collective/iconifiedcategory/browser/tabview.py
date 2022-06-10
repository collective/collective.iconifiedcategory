# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.eeafaceted.z3ctable.browser.views import ExtendedCSSTable
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.interfaces import ICategorizedConfidential
from collective.iconifiedcategory.interfaces import ICategorizedPrint
from collective.iconifiedcategory.interfaces import ICategorizedPublishable
from collective.iconifiedcategory.interfaces import ICategorizedSigned
from collective.iconifiedcategory.interfaces import ICategorizedTable
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from plone import api
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements

import html


class CategorizedTabView(BrowserView):

    def table_render(self, portal_type=None):
        self.portal_type = portal_type
        table = self.context.restrictedTraverse('@@iconifiedcategory_table')
        self.table = table
        self.table.portal_type = portal_type
        self._prepare_table_render()
        self.table.update()
        return self.table.render()

    def _prepare_table_render(self, **kwargs):
        if self.show('confidentiality'):
            alsoProvides(self.table, ICategorizedConfidential)
        if self.show('to_be_printed'):
            alsoProvides(self.table, ICategorizedPrint)
        if self.show('publishable'):
            alsoProvides(self.table, ICategorizedPublishable)
        if self.show('signed'):
            alsoProvides(self.table, ICategorizedSigned)

    def _config(self):
        """ """
        return utils.get_config_root(self.context)

    def show(self, action_type):
        """ """
        config = self._config()
        if config.portal_type == 'ContentCategoryConfiguration':
            return True
        attr_config = '{0}_activated'.format(action_type)
        show = getattr(config, attr_config) and self._show_column(action_type)
        return show

    def _show_column(self, action_type):
        """Made to be overrided."""
        return True


class CategorizedContent(object):

    def __init__(self, context, content):
        self.context = context
        self.UID = content['UID']
        self._metadata = context.categorized_elements.get(content['UID'], {})

    def __getattr__(self, key):
        if key in self._metadata:
            return self._metadata.get(key)
        return getattr(self.context, key)

    def getObject(self):
        obj = getattr(self, 'obj', None)
        if not obj:
            obj = self.context.get(self._metadata['id'])
            self.obj = obj
        return obj

    # make call to _unrestrictedGetObject behaves like getObject
    _unrestrictedGetObject = getObject

    @property
    def Description(self):
        return self.getObject().Description()

    @property
    def Creator(self):
        return self.getObject().Creator()

    @property
    def CreationDate(self):
        return self.created

    @property
    def created(self):
        return self.getObject().created()

    @property
    def ModificationDate(self):
        return self.modified

    @property
    def modified(self):
        return self.getObject().modified()

    def getPath(self):
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        path = '{0}/{1}'.format(portal_path, self.relative_url)
        return path

    def getURL(self, suffix=None):
        """ """
        portal_url = api.portal.get().absolute_url()
        suffix = suffix or self.relative_url
        return portal_url + '/' + suffix


class CategorizedTable(ExtendedCSSTable, BrowserView):
    implements(ICategorizedTable)

    cssClasses = {'table': 'listing iconified-listing nosort'}

    cssClassEven = u'odd'
    cssClassOdd = u'even'
    # do not sort, keep order of position in parent
    sortOn = None
    batchSize = 999
    startBatchingAt = 999

    def __init__(self, context, request, portal_type=None):
        """If received, this let's filter table for a given portal_type."""
        self.portal_type = portal_type
        super(CategorizedTable, self).__init__(context, request)
        self.portal = api.portal.get()

    @property
    def values(self):
        if not getattr(self, '_v_stored_values', []):
            sort_on = 'getObjPositionInParent'
            sort_categorized_tab = api.portal.get_registry_record(
                'sort_categorized_tab',
                interface=IIconifiedCategorySettings,
            )
            if sort_categorized_tab is True:
                sort_on = None
            data = [
                CategorizedContent(self.context, content) for content in
                utils.get_categorized_elements(
                    self.context,
                    result_type='dict',
                    portal_type=self.portal_type,
                    sort_on=sort_on,
                )
            ]
            self._v_stored_values = data
        return self._v_stored_values

    def render(self):
        if not len(self.rows):
            return _(
                'no_element_to_display',
                default="<span class='discreet iconified_category_no_element'>No element to display.</span>")
        return super(CategorizedTable, self).render()


class TitleColumn(BaseColumn):
    header = _(u'Title')
    weight = 20
    attrName = 'title'
    # we manage escape here manually
    escape = False

    def renderCell(self, content):
        pattern = (
            u'<a href="{link}" alt="{title}" title="{title}" target="{target}">'
            u'<img src="{icon}" alt="{category}" title="{category}" />'
            u' {title}</a><p class="discreet">{description}</p>'
        )
        url = content.getURL()
        target = ''
        if content.preview_status == 'converted':
            url = u'{0}/documentviewer#document/p1'.format(url)
            target = '_blank'
        return pattern.format(
            link=url,
            title=html.escape(getattr(content, self.attrName).decode('utf-8')),
            target=target,
            icon=content.icon_url,
            category=html.escape(safe_unicode(content.category_title)),
            description=html.escape(safe_unicode(content.Description)),
        )


class CategoryColumn(BaseColumn):
    header = _(u'Category')
    weight = 30
    attrName = 'category_title'
    escape = False

    def renderCell(self, content):
        category_title = safe_unicode(content.category_title)
        if content.subcategory_title:
            category_title = u"{0} / {1}".format(category_title,
                                                 safe_unicode(content.subcategory_title))
        return html.escape(category_title)


class AuthorColumn(BaseColumn):
    header = _(u'Author')
    weight = 40

    def renderCell(self, content):
        return html.escape(content.Creator)


class CreationDateColumn(BaseColumn):
    header = _(u'Creation date')
    weight = 50

    def renderCell(self, content):
        return api.portal.get_localized_time(
            datetime=content.created,
            long_format=True,
        )


class LastModificationColumn(BaseColumn):
    header = _(u'Last modification')
    weight = 60

    def renderCell(self, content):
        if content.created == content.modified:
            return ''
        return api.portal.get_localized_time(
            datetime=content.modified,
            long_format=True,
        )


class FilesizeColumn(BaseColumn):
    header = _(u'Filesize')
    weight = 70
    escape = False

    def renderHeadCell(self):
        """ """
        header = super(FilesizeColumn, self).renderHeadCell()
        total = sum([v.filesize for v in self.table.values
                     if v.filesize is not None])
        header += u"<p>(Total: {0})</p>".format(utils.render_filesize(total))
        return header

    def renderCell(self, content):
        if getattr(content, 'filesize', None) is None:
            return ''
        return utils.render_filesize(content.filesize)


class IconClickableColumn(BaseColumn):
    action_view = ''
    escape = False

    def _deactivated_is_useable(self):
        '''Is deactivated value a useable one?'''
        return False

    def get_url(self, content):
        if not self._deactivated_is_useable() and self.is_deactivated(content):
            return '#'
        return '{url}/@@{action}'.format(
            url=content.getURL(),
            action=self.get_action_view(content),
        )

    def get_action_view(self, content):
        return self.action_view

    def alt(self, content):
        return self.header

    def is_deactivated(self, content):
        return getattr(content, self.attrName, False) is None

    def is_editable(self, content):
        view = getMultiAdapter((content.getObject(), self.request), name=self.action_view)
        return view._may_set_values({})

    def is_active(self, content):
        return getattr(content, self.attrName, False)

    def css_class(self, content):
        is_deactivated = self.is_deactivated(content)
        if not self._deactivated_is_useable() and is_deactivated:
            return ' deactivated'
        base_css = self.is_active(content) and ' active' or ''
        if is_deactivated:
            base_css = ' deactivated' + base_css
        if self.is_editable(content):
            return '{0} editable'.format(base_css)
        return base_css

    def renderCell(self, content):
        link = (u'<a href="{0}" class="iconified-action{1}" alt="{2}" '
                u'title="{2}"></a>')
        return link.format(
            self.get_url(content),
            self.css_class(content),
            self.alt(content),
        )


class PrintColumn(IconClickableColumn):
    header = _(u'To be printed')
    cssClasses = {'td': 'iconified-print'}
    weight = 80
    attrName = 'to_print'
    action_view = 'iconified-print'

    def alt(self, content):
        return translate(
            utils.print_message(content),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )


class ConfidentialColumn(IconClickableColumn):
    header = _(u'Confidential')
    cssClasses = {'td': 'iconified-confidential'}
    weight = 90
    attrName = 'confidential'
    action_view = 'iconified-confidential'

    def alt(self, content):
        return translate(
            utils.boolean_message(content, attr_name='confidential'),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )


class SignedColumn(IconClickableColumn):
    header = _(u'Signed')
    cssClasses = {'td': 'iconified-signed'}
    weight = 95
    attrName = 'signed'
    action_view = 'iconified-signed'

    def alt(self, content):
        return translate(
            utils.signed_message(content),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )

    def _deactivated_is_useable(self):
        '''Is deactivated value a useable one?'''
        return True

    def is_deactivated(self, content):
        return not getattr(content, 'to_sign', True)


class PublishableColumn(IconClickableColumn):
    header = _(u'Publishable')
    cssClasses = {'td': 'iconified-publishable'}
    weight = 98
    attrName = 'publishable'
    action_view = 'iconified-publishable'

    def alt(self, content):
        return translate(
            utils.boolean_message(content, attr_name='publishable'),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )


class ActionColumn(BaseColumn):
    header = u''
    weight = 100
    escape = False

    def renderCell(self, content):
        link = u'<a href="{href}"><img src="{src}" title="{title}" /></a>'
        render = []
        if _checkPermission(ModifyPortalContent, content):
            render.append(link.format(
                href=u'{0}/edit'.format(content.getURL()),
                src=u'{0}/edit.gif'.format(content.getURL()),
                title=_('Edit'),
            ))
        if content.download_url:
            render.append(link.format(
                href=content.download_url,
                src=u'{0}/download_icon.png'.format(content.getURL()),
                title=_('Download'),
            ))
        if content.preview_status == 'converted':
            render.append(link.format(
                href=u'{0}/documentviewer#document/p1'.format(content.getURL()),
                src=u'{0}/file_icon.png'.format(content.getURL()),
                title=_('Preview'),
            ))
        return u''.join(render)
