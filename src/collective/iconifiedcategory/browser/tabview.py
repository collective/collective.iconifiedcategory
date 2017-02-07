# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Products.Five import BrowserView
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone.utils import safe_unicode
from plone import api
from z3c.table.table import Table
from z3c.table import column
from zope.i18n import translate
from zope.interface import implements
from zope.interface import alsoProvides

from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.interfaces import ICategorizedConfidential
from collective.iconifiedcategory.interfaces import ICategorizedPrint
from collective.iconifiedcategory.interfaces import ICategorizedTable
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings


class CategorizedTabView(BrowserView):

    def table_render(self, portal_type=None):
        table = CategorizedTable(self.context, self.request, portal_type=portal_type)
        self._prepare_table_render(table, portal_type)
        table.update()
        return table.render()

    def _prepare_table_render(self, table, portal_type):
        alsoProvides(table, ICategorizedPrint)
        alsoProvides(table, ICategorizedConfidential)


class CategorizedContent(object):

    def __init__(self, brain, context):
        self._obj = brain
        self._metadata = context.categorized_elements.get(brain.UID, {})

    def __getattr__(self, key):
        if key in self._metadata:
            return self._metadata.get(key)
        try:
            return getattr(self._obj, key)
        except AttributeError:
            return self.__getattribute__(key)

    def real_object(self):
        if not hasattr(self, '_real_object'):
            self._real_object = self._obj.getObject()
        return self._real_object


class CategorizedTable(Table):
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

    @property
    def values(self):
        sort_on = 'getObjPositionInParent'
        sort_categorized_tab = api.portal.get_registry_record(
            'sort_categorized_tab',
            interface=IIconifiedCategorySettings,
        )
        if sort_categorized_tab is True:
            sort_on = None
        return [
            CategorizedContent(content, self.context) for content in
            utils.get_categorized_elements(
                self.context,
                result_type='brains',
                portal_type=self.portal_type,
                sort_on=sort_on,
            )
        ]

    def render(self):
        if not len(self.rows):
            return _(
                'no_element_to_display',
                default="<span class='discreet iconified_category_no_element'>No element to display.</span>")
        return super(CategorizedTable, self).render()


class TitleColumn(column.GetAttrColumn):
    header = _(u'Title')
    weight = 20
    attrName = 'title'

    def renderCell(self, obj):
        content = (
            u'<a href="{link}" alt="{title}" title="{title}" target="{target}">'
            u'<img src="{icon}" alt="{category}" title="{category}" />'
            u' {title}</a><p class="discreet">{description}</p>'
        )
        url = obj.getURL()
        target = ''
        if obj.preview_status == 'converted':
            url = u'{0}/documentviewer#document/p1'.format(url)
            target = '_blank'
        return content.format(
            link=url,
            title=getattr(obj, self.attrName).decode('utf-8'),
            target=target,
            icon=obj.icon_url,
            category=safe_unicode(obj.category_title),
            description=safe_unicode(obj.Description),
        )


class CategoryColumn(column.GetAttrColumn):
    header = _(u'Category')
    weight = 30
    attrName = 'category_title'

    def renderCell(self, obj):
        category_title = safe_unicode(obj.category_title)
        if obj.subcategory_title:
            category_title = u"{0} / {1}".format(category_title,
                                                 safe_unicode(obj.subcategory_title))
        return category_title


class AuthorColumn(column.GetAttrColumn):
    header = _(u'Author')
    weight = 40

    def renderCell(self, obj):
        return obj.Creator


class CreationDateColumn(column.GetAttrColumn):
    header = _(u'Creation date')
    weight = 50

    def renderCell(self, obj):
        return api.portal.get_localized_time(
            datetime=obj.created,
            long_format=True,
        )


class LastModificationColumn(column.GetAttrColumn):
    header = _(u'Last modification')
    weight = 60

    def renderCell(self, obj):
        if obj.created == obj.modified:
            return ''
        return api.portal.get_localized_time(
            datetime=obj.modified,
            long_format=True,
        )


class FilesizeColumn(column.GetAttrColumn):
    header = _(u'Filesize')
    weight = 70

    def renderCell(self, obj):
        if getattr(obj, 'filesize', None) is None:
            return ''
        return utils.render_filesize(obj.filesize)


class IconClickableColumn(column.GetAttrColumn):
    action_view = ''

    def get_url(self, obj):
        if self.is_deactivated(obj):
            return '#'
        return '{url}/@@{action}'.format(
            url=obj.getURL(),
            action=self.get_action_view(obj),
        )

    def get_action_view(self, obj):
        return self.action_view

    def alt(self, obj):
        return self.header

    def is_deactivated(self, obj):
        return getattr(obj, self.attrName, False) is None

    def is_editable(self, obj):
        return _checkPermission(ModifyPortalContent,
                                obj.real_object())

    def css_class(self, obj):
        if self.is_deactivated(obj):
            return ' deactivated'
        base_css = getattr(obj, self.attrName, False) and ' active' or ''
        if self.is_editable(obj):
            return '{0} editable'.format(base_css)
        return base_css

    def renderCell(self, obj):
        link = (u'<a href="{0}" class="iconified-action{1}" alt="{2}" '
                u'title="{2}"></a>')
        return link.format(
            self.get_url(obj),
            self.css_class(obj),
            self.alt(obj),
        )


class PrintColumn(IconClickableColumn):
    header = _(u'To be printed')
    cssClasses = {'td': 'iconified-print'}
    weight = 80
    attrName = 'to_print'
    action_view = 'iconified-print'

    def alt(self, obj):
        return translate(
            utils.print_message(obj),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )


class ConfidentialColumn(IconClickableColumn):
    header = _(u'Confidential')
    cssClasses = {'td': 'iconified-confidential'}
    weight = 90
    attrName = 'confidential'
    action_view = 'iconified-confidential'

    def alt(self, obj):
        return translate(
            utils.confidential_message(obj),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )


class ActionColumn(column.GetAttrColumn):
    header = u''
    weight = 100

    def renderCell(self, obj):
        link = u'<a href="{href}"><img src="{src}" title="{title}" /></a>'
        render = []
        if _checkPermission(ModifyPortalContent, obj):
            render.append(link.format(
                href=u'{0}/edit'.format(obj.getURL()),
                src=u'{0}/edit.gif'.format(obj.getURL()),
                title=_('Edit'),
            ))
        if obj.download_url:
            render.append(link.format(
                href=obj.download_url,
                src=u'{0}/download_icon.png'.format(obj.getURL()),
                title=_('Download'),
            ))
        if obj.preview_status == 'converted':
            render.append(link.format(
                href=u'{0}/documentviewer#document/p1'.format(obj.getURL()),
                src=u'{0}/file_icon.png'.format(obj.getURL()),
                title=_('Preview'),
            ))
        return u''.join(render)
