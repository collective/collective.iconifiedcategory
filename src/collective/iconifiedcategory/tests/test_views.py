# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective import iconifiedcategory as collective_iconifiedcategory
from collective.iconifiedcategory import HAS_DOCUMENTVIEWER
from collective.iconifiedcategory.behaviors.iconifiedcategorization import (
    IIconifiedCategorizationMarker,
)
from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.tests.adapters import TestingCategorizedObjectAdapter
from collective.iconifiedcategory.tests.base import BaseTestCase
from collective.iconifiedcategory.tests.base import skip_without_documentviewer
from collective.iconifiedcategory.utils import get_category_icon_url
from collective.iconifiedcategory.utils import get_category_object
from DateTime import DateTime
from OFS.interfaces import IItem
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing.interfaces import TEST_USER_NAME
from Products.CMFCore.permissions import View
from zope.configuration import xmlconfig
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.browser import IBrowserRequest

import transaction


def _restrict_view_and_trust_can_view(testcase, obj):
    """Remove View from obj for the test user but let IIconifiedContent.can_view
    grant access to non confidential elements."""
    testcase.register_adapter(
        TestingCategorizedObjectAdapter,
        (IItem, IBrowserRequest, IIconifiedCategorizationMarker),
        IIconifiedContent,
    )
    obj.manage_permission(View, ["Manager"])
    login(testcase.portal, TEST_USER_NAME)
    testcase.assertFalse(api.user.get_current().has_permission(View, obj))


if HAS_DOCUMENTVIEWER:
    from collective.documentviewer.settings import GlobalSettings


class TestCategorizedChildView(BaseTestCase):

    def setUp(self):
        super(TestCategorizedChildView, self).setUp()
        api.content.create(
            id="docB",
            type="Document",
            title="B",
            container=self.portal,
            content_category="config_-_group-1_-_category-1-2",
            to_print=False,
            confidential=False,
        )
        api.content.create(
            id="docA",
            type="Document",
            title="A",
            container=self.portal,
            content_category="config_-_group-1_-_category-1-2",
            to_print=False,
            confidential=False,
        )
        self.view = self.portal.restrictedTraverse("@@categorized-childs")
        self.view.portal_type = None

    def tearDown(self):
        super(TestCategorizedChildView, self).tearDown()
        elements = ("docB", "docA")
        for element in elements:
            if element in self.portal:
                api.content.delete(self.portal[element])

    def test__call__(self):
        category = get_category_object(
            self.portal.file_txt, self.portal.file_txt.content_category
        )
        scale = category.restrictedTraverse("@@images").scale(scale="listing").__name__
        # the category and elements of category is displayed
        result = self.view()
        self.assertTrue(
            '<img width="16px" height="16px" src="{0}/@@images/{1}"'.format(
                category.absolute_url(), scale
            )
            in result
        )

        # remove the categorized elements
        api.content.delete(self.portal["file_txt"])
        api.content.delete(self.portal["image"])
        api.content.delete(self.portal["docB"])
        api.content.delete(self.portal["docA"])
        self.assertEqual(self.view().strip(), '<span class="discreet">Nothing.</span>')

    def test_categories_infos(self):
        self.view()
        infos = self.view.categories_infos()
        self.assertEqual(2, len(infos))
        self.assertEqual("category-1-1", infos[1]["id"])
        self.assertEqual(2, infos[0]["counts"])


class TestManageCategorizedChildView(BaseTestCase):

    def test_get_management_url(self):
        view = self.portal.restrictedTraverse("@@categorized-childs-manage")
        self.assertEqual(
            view.get_management_url(), "http://nohost/plone/@@iconifiedcategory"
        )
        self.assertIn('href="http://nohost/plone/@@iconifiedcategory"', view())

    def test__call__(self):
        """The Font Awesome glyph of Plone 4 is an icon of the icon resolver."""
        view = self.portal.restrictedTraverse("@@categorized-childs-manage")
        self.assertIn('class="plone-icon manage-categorized-elements', view())


class TestCategorizedChildInfosView(TestCategorizedChildView):

    def setUp(self):
        super(TestCategorizedChildInfosView, self).setUp()
        self.viewinfos = self.portal.restrictedTraverse("@@categorized-childs-infos")
        category_uid = self.config["group-1"]["category-1-1"].UID()
        self.viewinfos(category_uid, filters={})

    def test__call__(self):
        # the category and elements of category is displayed
        self.viewinfos.update()
        result = self.viewinfos.index()
        self.assertTrue(
            '<a class="categorized-element-title" href="http://nohost/plone/image/@@download">'
            in result
        )
        self.assertTrue('<span title="File description">file.txt</span>' in result)
        self.assertTrue(
            '<a class="categorized-element-title" href="http://nohost/plone/image/@@download">'
            in result
        )
        self.assertTrue(
            '<span title="Image description">ic\xf4ne1.png</span>' in result
        )

        # in case a file is too large, a warning is displayed
        # manipulate stored categorized_elements
        self.portal.categorized_elements[self.portal["file_txt"].UID()][
            "warn_filesize"
        ] = True
        self.portal.categorized_elements[self.portal["file_txt"].UID()][
            "filesize"
        ] = 7000000
        self.viewinfos.update()
        self.assertTrue(
            "(<span class='warn_filesize' title='Annex size is huge, "
            "it could be difficult to be downloaded!'>6.7 MB</span>)"
            in self.viewinfos.index()
        )

        # remove the categorized elements
        api.content.delete(self.portal["file_txt"])
        api.content.delete(self.portal["image"])
        api.content.delete(self.portal["docB"])
        api.content.delete(self.portal["docA"])
        self.viewinfos.update()
        self.assertEqual(self.viewinfos.index(), "\n")

    def test_preview_status_icons(self):
        """The Plone 4 skin image spinner_small.gif is an icon of the icon resolver."""
        infos = self.portal.categorized_elements[self.portal["file_txt"].UID()]
        infos["preview_status"] = "in_progress"
        self.viewinfos.update()
        self.assertIn(
            'src="http://nohost/plone/@@iconresolver/hourglass-split"',
            self.viewinfos.index(),
        )
        infos["preview_status"] = "conversion_error"
        self.viewinfos.update()
        self.assertIn(
            'src="http://nohost/plone/@@iconresolver/plone-error"',
            self.viewinfos.index(),
        )

    def test_categories_uids(self):
        self.viewinfos.update()
        self.assertEqual(
            [self.viewinfos.category_uid],
            self.viewinfos.categories_uids,
        )
        self.viewinfos.category_uid = self.config["group-1"]["category-1-2"].UID()
        self.viewinfos.update()
        self.assertEqual(
            [self.viewinfos.category_uid],
            self.viewinfos.categories_uids,
        )

    def test_infos(self):
        self.viewinfos.update()
        infos = self.viewinfos.infos()
        self.assertCountEqual([self.viewinfos.category_uid], list(infos.keys()))
        self.assertCountEqual(
            ["file.txt", "icône1.png"],
            [e["title"] for e in infos[self.viewinfos.category_uid]],
        )

        self.viewinfos.category_uid = self.config["group-1"]["category-1-2"].UID()
        self.viewinfos.update()
        infos = self.viewinfos.infos()
        self.assertCountEqual([self.viewinfos.category_uid], list(infos.keys()))
        self.assertCountEqual(
            ["A", "B"],
            [e["title"] for e in infos[self.viewinfos.category_uid]],
        )

    def test_filters(self):
        self.viewinfos.update()
        self.assertEqual(len(self.viewinfos.categorized_elements), 2)
        self.viewinfos.filters["id"] = "file_txt"
        self.viewinfos.update()
        self.assertEqual(len(self.viewinfos.categorized_elements), 1)
        self.assertEqual(self.viewinfos.categorized_elements[0]["id"], "file_txt")
        # filters are passed to viewinfos as json
        self.viewinfos(
            category_uid=self.viewinfos.category_uid, filters={"id": "image"}
        )
        self.assertEqual(len(self.viewinfos.categorized_elements), 1)
        self.assertEqual(self.viewinfos.categorized_elements[0]["id"], "image")

    @skip_without_documentviewer
    def test_show_preview(self):
        infos = self.portal.restrictedTraverse("@@categorized-childs-infos")
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_convert = False
        gsettings.auto_layout_file_types = ["pdf"]
        category_group = self.portal.config.get("group-1")
        category = category_group.get("category-1-1")
        category_uid = category.UID()
        file1 = api.content.create(
            id="file1",
            type="File",
            file=self.file_pdf,
            container=self.portal,
            content_category="config_-_group-1_-_category-1-1",
            to_print=False,
            confidential=False,
        )
        # show_preview=0, default element was not converted
        element = self.portal.categorized_elements[file1.UID()]
        self.assertEqual(element["show_preview"], 0)
        self.assertEqual(element["preview_status"], "not_converted")
        self.assertFalse("/file1/documentviewer#document/p1" in infos(category_uid, {}))
        self.assertTrue("/file1/@@download" in infos(category_uid, {}))
        # show_preview=1, element is converted and download is still possible
        category.show_preview = 1
        file2 = api.content.create(
            id="file2",
            type="File",
            file=self.file_pdf,
            container=self.portal,
            content_category="config_-_group-1_-_category-1-1",
            to_print=False,
            confidential=False,
        )
        element = self.portal.categorized_elements[file2.UID()]
        self.assertEqual(element["show_preview"], 1)
        self.assertEqual(element["preview_status"], "converted")
        self.assertTrue("/file2/documentviewer#document/p1" in infos(category_uid, {}))
        self.assertTrue("/file2/@@download" in infos(category_uid, {}))
        # show_preview=2, element is converted and download can be protected
        category.show_preview = 2
        file3 = api.content.create(
            id="file3",
            type="File",
            file=self.file_pdf,
            container=self.portal,
            content_category="config_-_group-1_-_category-1-1",
            to_print=False,
            confidential=False,
        )
        element = self.portal.categorized_elements[file3.UID()]
        self.assertEqual(element["show_preview"], 2)
        self.assertEqual(element["preview_status"], "converted")
        self.assertTrue("/file3/documentviewer#document/p1" in infos(category_uid, {}))
        self.assertTrue("/file3/@@download" in infos(category_uid, {}))


class TestCanViewAwareDownload(BaseTestCase):

    def test_default(self):
        # by default @@download returns the file, here
        # it is also the case as IIconifiedContent.can_view adapter returns True by default
        file_obj = self.portal["file_txt"]
        img_obj = self.portal["image"]
        self.assertTrue(file_obj.restrictedTraverse("@@download")())
        self.assertTrue(file_obj.restrictedTraverse("@@display-file")())
        self.assertTrue(
            file_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.file/@@download"
            )()
        )
        self.assertTrue(img_obj.restrictedTraverse("@@download")())
        self.assertTrue(img_obj.restrictedTraverse("@@display-file")())
        self.assertTrue(
            img_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.image/@@download"
            )()
        )
        # make file_obj not downloadable
        file_obj.manage_permission(
            View,
            [
                "Manager",
            ],
        )
        login(self.portal, TEST_USER_NAME)
        self.assertFalse(api.user.get_current().has_permission(View, file_obj))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@download"))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@display-file"))
        self.assertRaises(
            Unauthorized,
            file_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.file/@@download"
            ),
        )
        logout()
        self.assertFalse(api.user.get_current().has_permission(View, file_obj))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@download"))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@display-file"))
        self.assertRaises(
            Unauthorized,
            file_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.file/@@download"
            ),
        )

    def test_can_not_view(self):
        # register an adapter that will return False
        xmlconfig.file("testing-adapters.zcml", package=collective_iconifiedcategory)
        file_obj = self.portal["file_txt"]
        img_obj = self.portal["image"]
        # downloadable when element is not confidential
        self.assertFalse(file_obj.confidential)
        self.assertFalse(img_obj.confidential)
        self.assertTrue(file_obj.restrictedTraverse("@@download")())
        self.assertTrue(file_obj.restrictedTraverse("@@display-file")())
        self.assertTrue(
            file_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.file/@@download"
            )()
        )
        self.assertTrue(img_obj.restrictedTraverse("@@download")())
        self.assertTrue(img_obj.restrictedTraverse("@@display-file")())
        self.assertTrue(
            img_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.image/@@download"
            )()
        )
        # when confidential, check can_view is done
        file_obj.confidential = True
        img_obj.confidential = True
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@download"))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@display-file"))
        self.assertRaises(
            Unauthorized,
            file_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.file/@@download"
            ),
        )
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse("@@download"))
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse("@@display-file"))
        self.assertRaises(
            Unauthorized,
            img_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.image/@@download"
            ),
        )
        # when using show_preview == 2, download is disabled
        # ths widget is shown but downloading raises Unauthorized
        file_obj.confidential = False
        img_obj.confidential = False
        self.assertTrue(file_obj.restrictedTraverse("@@download")())
        self.assertTrue(img_obj.restrictedTraverse("@@download")())
        self.portal.categorized_elements[file_obj.UID()]["show_preview"] = 2
        self.portal.categorized_elements[img_obj.UID()]["show_preview"] = 2
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@download"))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@display-file"))
        self.assertTrue(
            file_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.file/@@download"
            )()
        )
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse("@@download"))
        self.assertRaises(Unauthorized, img_obj.restrictedTraverse("@@display-file"))
        self.assertTrue(
            img_obj.unrestrictedTraverse(
                "view/++widget++form.widgets.image/@@download"
            )()
        )

    def test_can_view_without_view_permission(self):
        """Access is managed by IIconifiedContent.can_view, not by the View permission."""
        file_obj = self.portal["file_txt"]
        _restrict_view_and_trust_can_view(self, file_obj)
        self.assertTrue(file_obj.restrictedTraverse("@@download")())
        self.assertTrue(file_obj.restrictedTraverse("@@display-file")())
        file_obj.confidential = True
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@download"))
        self.assertRaises(Unauthorized, file_obj.restrictedTraverse("@@display-file"))


class TestCanViewAwareFNWDownload(BaseTestCase):

    def test___call__(self):
        """The edit/view form widget download is managed by IIconifiedContent.can_view."""
        file_obj = self.portal["file_txt"]
        img_obj = self.portal["image"]
        _restrict_view_and_trust_can_view(self, file_obj)
        img_obj.manage_permission(View, ["Manager"])
        file_download = "view/++widget++form.widgets.file/@@download"
        img_download = "view/++widget++form.widgets.image/@@download"
        self.assertTrue(file_obj.unrestrictedTraverse(file_download)())
        self.assertTrue(img_obj.unrestrictedTraverse(img_download)())
        file_obj.confidential = True
        img_obj.confidential = True
        self.assertRaises(Unauthorized, file_obj.unrestrictedTraverse(file_download))
        self.assertRaises(Unauthorized, img_obj.unrestrictedTraverse(img_download))


class TestImageDataModifiedImageScaling(BaseTestCase):

    def test_modified(self):
        """The icon file modification date is used, not the category one,
        so editing a category does not change the icon url."""
        category = self.config["group-1"]["category-1-1"]
        transaction.commit()
        modified = category.restrictedTraverse("@@images").modified()
        self.assertEqual(modified, DateTime(category.icon._p_mtime).millis())
        icon_url = get_category_icon_url(category)
        # edit the category
        category.setTitle("Category 1-1 edited")
        notify(ObjectModifiedEvent(category))
        transaction.commit()
        self.assertNotEqual(category._p_mtime, category.icon._p_mtime)
        self.assertEqual(category.restrictedTraverse("@@images").modified(), modified)
        self.assertEqual(get_category_icon_url(category), icon_url)
        # change the icon
        category.icon = self.icon
        notify(ObjectModifiedEvent(category))
        transaction.commit()
        self.assertNotEqual(
            category.restrictedTraverse("@@images").modified(), modified
        )
        self.assertNotEqual(get_category_icon_url(category), icon_url)
