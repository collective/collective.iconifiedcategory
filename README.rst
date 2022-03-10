.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide_addons.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://github.com/collective/collective.iconifiedcategory/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/collective/collective.iconifiedcategory/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/github/collective/collective.iconifiedcategory/badge.svg
    :target: https://coveralls.io/github/collective/collective.iconifiedcategory

.. image:: http://img.shields.io/pypi/v/collective.iconifiedcategory.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/collective.iconifiedcategory


==============================================================================
collective.iconifiedcategory
==============================================================================

This product will let you categorize created content using a category identified by an icon.

A dexterity behavior can be enabled and will add a field "content category" that will list available categories defined in a configuration.

So you first have to define the categories by adding a ContentCategoryConfiguration somewhere.  Then add a CategoryGroup on which some extra features may be activated :

- is content confidential?
- is content an element to print?
- is content an element to sign?

If activated, these fields will be available on the content using the behavior.

Then into a CategoryGroup, you will be able to add ContentCategory that are characterized by a title and an icon.  These ContentCategory elements will be the terms of a vocabulary used to select a category on a content using the behavior.

This package is widely overridable and is made to manage many usecases of iconified categories.

A element that contains categorized content will display a special widget where categorized content are grouped by ContentCategory behind an icon.

A table view is also available listing categorized contents with more details.

Screenshots to come...

Installation
------------

Install collective.iconifiedcategory by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.iconifiedcategory


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.iconifiedcategory/issues
- Source Code: https://github.com/collective/collective.iconifiedcategory


License
-------

The project is licensed under the GPLv2.
