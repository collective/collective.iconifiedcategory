# -*- coding: utf-8 -*-
from plone import api
from plone.app.robotframework.remote import RemoteLibrary
from plone.app.robotframework.remote import RemoteLibraryLayer
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.robotframework.utils import disableCSRFProtection
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from plone.testing.zope import WSGI_SERVER_FIXTURE

import collective.iconifiedcategory


class CollectiveIconifedCategoryLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        z2.installProduct(app, 'Products.DateRecurringIndex')
        self.loadZCML(package=collective.iconifiedcategory)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.iconifiedcategory:testing')


COLLECTIVE_ICONIFIED_CATEGORY_FIXTURE = CollectiveIconifedCategoryLayer()


COLLECTIVE_ICONIFIED_CATEGORY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_ICONIFIED_CATEGORY_FIXTURE,),
    name='CollectiveIconifedCategoryLayer:IntegrationTesting'
)


COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_ICONIFIED_CATEGORY_FIXTURE,),
    name='CollectiveIconifedCategoryLayer:FunctionalTesting'
)


class IconifiedCategoryRemoteKeywords(RemoteLibrary):
    """Robot keywords of collective.iconifiedcategory, imported from ${PLONE_URL}/IconifiedCategoryRobotRemote."""

    def create_categorized_content(self, container_path, portal_type, title, content_category):
        """Create a categorized content like its add form does (the Create content keyword
           fails on the category field, its vocabulary needs a context), return its UID."""
        disableCSRFProtection()
        container = api.portal.get().unrestrictedTraverse(container_path)
        obj = api.content.create(
            container=container, type=portal_type, title=title, content_category=content_category)
        return obj.UID()

    def set_content_attribute(self, path, name, value):
        """Set an attribute of a content (path from the portal), without the CSRF check of Set field value."""
        disableCSRFProtection()
        obj = api.portal.get().unrestrictedTraverse(path)
        setattr(obj, name, value)
        obj.reindexObject()


ICONIFIED_CATEGORY_REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(IconifiedCategoryRemoteKeywords,),
    name='IconifiedCategoryRemoteLibrary:IconifiedCategoryRobotRemote'
)


COLLECTIVE_ICONIFIED_CATEGORY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_ICONIFIED_CATEGORY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        ICONIFIED_CATEGORY_REMOTE_LIBRARY_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name='CollectiveIconifedCategoryLayer:AcceptanceTesting'
)
