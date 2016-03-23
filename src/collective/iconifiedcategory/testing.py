# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

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


COLLECTIVE_ICONIFIED_CATEGORY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_ICONIFIED_CATEGORY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveIconifedCategoryLayer:AcceptanceTesting'
)
