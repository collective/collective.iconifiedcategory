# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""


class PreviewStatus(object):
    """
    Preview status class

    Valid status codes are:
        * not_convertable
        * in_progress
        * converted
        * conversion_error
    """
    _valid_codes = (
        'not_convertable',
        'in_progress',
        'converted',
        'conversion_error',
    )

    def __init__(self, code, message=None):
        if code not in self._valid_codes:
            raise ValueError("Unknown code '{0}'".format(code))
        self.code = code
        self.message = message

    @property
    def converted(self):
        return self.code == 'converted'
