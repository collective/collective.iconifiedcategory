# -*- coding: utf-8 -*-
"""Robot suites of tests/robot.

ROBOT_PLONE_MAJOR (4 or 6) selects the UI keywords: robotsuite passes the
ROBOT_* environment variables to the suites as robot variables.
"""
from collective.iconifiedcategory.testing import (
    COLLECTIVE_ICONIFIED_CATEGORY_ACCEPTANCE_TESTING,
)
from importlib.metadata import version
from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered

import os
import robotsuite
import unittest


def test_suite():
    os.environ.setdefault(
        "ROBOT_PLONE_MAJOR", version("Products.CMFPlone").split(".")[0]
    )
    suite = unittest.TestSuite()
    robot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot")
    for name in sorted(os.listdir(robot_dir)):
        if name.startswith("test_") and name.endswith(".robot"):
            robottestsuite = robotsuite.RobotTestSuite(os.path.join("robot", name))
            robottestsuite.level = ROBOT_TEST_LEVEL
            suite.addTests(
                [
                    layered(
                        robottestsuite,
                        layer=COLLECTIVE_ICONIFIED_CATEGORY_ACCEPTANCE_TESTING,
                    )
                ]
            )
    return suite
