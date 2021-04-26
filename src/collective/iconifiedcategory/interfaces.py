# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.iconifiedcategory import _
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager


class IBelowCategorizedElementsManager(IViewletManager):
    """A viewlet manager that sits just below categorized elements table."""


class ICollectiveIconifiedCategoryLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IIconifiedCategoryConfig(Interface):
    pass


class IIconifiedCategoryGroup(Interface):
    pass


class IIconifiedContent(Interface):
    pass


class IIconifiedInfos(Interface):
    pass


class IIconifiedPrintable(Interface):
    pass


class IIconifiedPreview(Interface):
    pass


class ICategorizedTable(Interface):
    pass


class ICategorizedPrint(ICategorizedTable):
    pass


class ICategorizedConfidential(ICategorizedTable):
    pass


class ICategorizedPublishable(ICategorizedTable):
    pass


class ICategorizedSigned(ICategorizedTable):
    pass


class IICImageScaleTraversable(IImageScaleTraversable):
    pass


class IIconifiedCategorySubtyper(Interface):

    have_categorized_elements = schema.Bool(
        u'Is current object contains categorized elements',
        readonly=True,
    )


class IIconifiedCategorySettings(Interface):

    sort_categorized_tab = schema.Bool(
        title=_(
            u'Sort categorized elements on categorized tab alphabetically '
            u'automatically. Uncheck to sort elements manually'),
        default=True,
    )

    categorized_childs_infos_columns_threshold = schema.Int(
        title=_(u'Maximum number of elements to display by columns when '
                u'displaying categorized elements of same category in the '
                u'tooltipster widget'),
        default=25,
    )

    filesizelimit = schema.Int(
        title=_(u'Filesize limit in bytes enabling a warning'),
        description=_(u'If the categorized element is a file, the user will '
                      u'get a warning whenever the filesize is bigger than '
                      u'defined value. <span style="color: red">Take care that '
                      u'if you change this value, you will have to update the '
                      u'categoized elements stored informations.</span> '),
        default=5000000,
    )


# Events

class ICategorizedElementsUpdatedEvent(IObjectEvent):
    pass


class IIconifiedAttrChangedEvent(IObjectEvent):

    attr_name = Attribute("The attribute name")
    old_values = Attribute("The old values")
    new_values = Attribute("The new values")


class IIconifiedModifiedEvent(IObjectEvent):
    pass


class IIconifiedCategoryChangedEvent(IObjectEvent):
    pass
