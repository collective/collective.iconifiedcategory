Changelog
=========

0.44 (2020-05-08)
-----------------

- Do no more make the elements using behavior marked with
  `IIconifiedCategorization` or `content_category.setter` is not working
  anymore.
  [gbastien]

0.43 (2020-04-30)
-----------------

- Adapted tests to use `file_txt` instead `file` as id for default `File`
  as `file` is also the name of the field, `portal.file` returns the `File`
  instance instead breaking because it does not have a `file` field.
  [gbastien]
- Do not break in `utils.validateFileIsPDF` while creating a new element and
  no file has been selected.
  [gbastien]

0.42 (2020-04-29)
-----------------

- Added parameter `use_category_uid_as_token=False` to
  `CategoryVocabulary.__call__` method to be able to use category/subcategory
  as term token instead the calculated content_id (default).
  [gbastien]


0.41 (2020-03-12)
-----------------

- Factorized events triggered when a categorized element attribute is changed
  (`to_print`, `confidential`, ...).  Now a single `IIconifiedAttrChangedEvent`
  event is triggered.  Moreover it is optimized to avoid too much process.
  [gbastien]
- Removed specific call to `IconifiedAttrChangedEvent('confidential')`
  when creating a new categorized element.
  [gbastien]
- Added `ICategorize.only_pdf` parameter making it possible to define if the
  categorized element is a file, that it can only be PDF.  Added also invariant
  on `IIconifiedCategorization` checking if file is a PDF when categorized
  element has a file field and used content_category has `only_pdf=True`.
  [gbastien]

0.40 (2020-02-18)
-----------------

- Make appearance of column in `CategorizedTabView` coherent with appearance of
  detail icon in `@@categorized-childs-infos` view,
  rely in both case on `CategorizedChildInfosView.show`
  [gbastien]

0.39 (2019-11-26)
-----------------

- Added management of `publishable` attribute like it is the case for `to_print`
  or `confidential` attributes.  Factorized when possible.
  [gbastien]

0.38 (2019-08-23)
-----------------

- Fixed code to work with `plone.app.async` as in this case, there is no
  `REQUEST`.  To do this, needed to get the `@@images` view by instantiating the
  `ImageDataModifiedImageScaling` class, this could be a problem if it is
  overrided by a subpackage.
  [gbastien]
- Tried to fix again tooltipster popup when categorized element title is
  displayed on several lines...
  [gbastien]

0.37 (2019-06-14)
-----------------

- Avoid vertical scroll in tooltipster popup when categorized content title
  is displayed on several lines.
  [gbastien]
- Force use distribution trusty in Travis.
  [gbastien]

0.36 (2019-04-23)
-----------------

- Overrided `ImageScaling.modified` to take into account real stored icon file
  `_p_mtime` instead category `_p_mtime` because the category's `_p_mtime` can
  be modified for several reasons and that breaks existing content using the
  icon. Moreover, it is now necessary to update elements using a category only
  when icon file changed.
  [gbastien]
- Force display small icon in select2 droprown so it fits the available space,
  this is the case when a large icon was uploaded.  Added description on field
  `ContentCategory.icon` explaining to use a 16x16 image icon.
  [gbastien]

0.35 (2019-02-22)
-----------------

- Use ram.cache for utils.get_ordered_categories to cache during a REQUEST.
  [gbastien]
- Added parameter `only_enabled (True by default)` when
  `using utils.get_ordered_categories` and
  `IconifiedCategoryGroupAdapter.get_every_categories` to be able to have every
  categories in utils.sort_categorized_elements.
  [gbastien]
- Use generated url for `scale mini` as icon url so it can be cached.
  [gbastien]
- Trigger `CategorizedElementsUpdatedEvent` after elements using a
  ContentCategory have been updated.
  [gbastien]
- Use `natsorted` instead `realsorted` to sort annexes by title.
  [gbastien]
- Updated upgrade step as step to 2100 should be done before step to 2000...
  Removed step to 2000 and integrated it into step to 2100 so we first compute
  ContentCategory icon listing scale then update every categorized elements.
  [gbastien]

0.34 (2019-01-31)
-----------------

- Display `content_category` title at the top of `@@categorized-childs-infos`
  tooltipster view.
  [gbastien]
- Use `natsort.realsorted` to sort categorized elements on their title,
  elements are sorted regardless of uppercase or lowercase title.
  [gbastien]
- Moved `context._p_changed = True` to the `utils.sort_categorized_elements`
  method so we are sure that calling it will correctly manage `_p_changed`.
  [gbastien]

0.33 (2018-08-03)
-----------------

- Adapted CSS regarding `FontAwesome` where font name changed in version 5+
  from `FontAwesome` to `Font Awesome 5 Free`.
  Require `collective.fontawesome >= 1.1`.
  [gbastien]

0.32 (2018-05-04)
-----------------

- Added `many_elements_7_columns` and `many_elements_8_columns` styles necessary
  when displaying really many elements on several columns.
  [gbastien]
- Make sure the icon sticks to the text first word in the tooltipster popup
  by wrapping the icon and categorized element title first word in a `<span>`
  that uses a `style="white-space: nowrap"`.
  [gbastien]

0.31 (2018-05-03)
-----------------

- Fix CSS applied in tooltipster popup for active confidential.
  [gbastien]

0.30 (2018-04-20)
-----------------

- Make sure number of elements applied CSS is done when tooltipstered or not.
  [gbastien]
- Added possibility to pass a CSS selector to `categorizedChildsInfos`, the JS
  method that initialize `tooltipster` for categorized elements.
  [gbastien]

0.29 (2018-02-14)
-----------------

- Adapted JS call to `tooltipster` as `collective.js.tooltipster` now uses
  `tooltipster` 4.2.6.  Require `collective.js.tooltipster` > 0.1
  [gbastien]

0.28 (2018-01-23)
-----------------

- When changing an element's `content_category`, reapply the default values for
  fields `to_print`, `confidential`, `to_sign` and `signed` if it was still the
  original default value defined on original `content_category`.  Default values
  are linked to the `content_category`.
  [gbastien]

0.27 (2017-12-07)
-----------------

- In `actionview.BaseView`, moved the `ObjectModifiedEvent` from the `__call__`
  to the `set_values` method so using it directly updates the
  `categorized_elements` of the parent.
  [gbastien]

0.26 (2017-11-29)
-----------------

- Use a specific static resourceDirectory for images.
  [gbastien]

0.25 (2017-11-28)
-----------------

- Call `actionview._may_set_values` in `IconClickableColumn.is_editable`
  to avoid double logic.
  [gbastien]

0.24 (2017-11-27)
-----------------

- Fixed migration that adds `to_sign/signed` relevant data to the
  `categorized_elements` of the parent containing categorized contents.
  Execute the update with `limited=False` and do not care about already
  migrated content, do the update on every found elements.
  [gbastien]
- Added tests for the `SignedChangeView` view especially the `loop` among
  possible `to_sign/signed` combination values.
  [gbastien]
- Do not break when deleting an element having a `content_category` if container
  does not have the `categorized_elements` dict.
  [gbastien]
- Improved some translations.
  [gbastien]
- Factorized the way categories and subcategories are get for the 
  `content_category` vocabularies `collective.iconifiedcategory.categories` and
  `collective.iconifiedcategory.category_titles` so it is easy to override and
  we rely on same method for both vocabularies that needs same source.
  [gbastien]

0.23 (2017-08-10)
-----------------

- Added management of `to_sign` and `signed` attributes like it is the case for
  `to_print` and `confidential` attributes.  Both attributes are used behind a
  single action `signed` that have 3 options : `not to sign`, `to sign` and
  `signed`.
  [gbastien]
- Default values for `to_print`, `confidential` and `to_sign/signed` are now
  managed in the `IObjectAddedEvent` no more in the `content_category setter`,
  this way every attribtues are managed the same way because `to_print` and
  `confidential` are simple attributes where `to_sign/signed` can come from the
  `Scan metadata` behavior of `collective.dms.scanbehavior`.
  [gbastien]
- Added possibility to show/hide details about `to_print`, `confidential`,
  `to_sign/signed` in the categorized elements tooltipster.

0.22 (2017-08-04)
-----------------

- Make portal available on the tabview instance.
  [gbastien]

0.21 (2017-07-18)
-----------------

- Reverted changes from releases `0.19` and `0.20`, we do not bypass can_view if
  element is not `confiential` because `can_view` could take into account other
  elements than `confidential`.
  [gbastien]

0.20 (2017-07-14)
-----------------

- Make sure we correctly bypass `can_view` in `utils._check_van_view` when
  element is not confidential in case we do not receive `obj` but
  `categorized_elements`.
  [gbastien]

0.19 (2017-07-13)
-----------------

- Factorized call to _check_can_view from utils and views so we are sure that
  the check is only done if obj is confidential.  This fix a bug where can_view
  check was done for not confidential obj and raised an error on @@download even
  though it was displayed in the categorized elements table.
  [gbastien]

0.18 (2017-05-29)
-----------------

- Added missing translation when updating categorized elements using the
  @@update-categorized-elements view.
  [gbastien]
- Use icon_expr instead content_icon on the types fti to define the icon.
  Actually we want to define no icon as the type icon is displayed using CSS.
  [gbastien]
- Added one additional level to the `content_category` generated by
  `utils.calculate_category_id` to avoid same `content_category` generated for
  different category group.
  [gbastien]
- Added parameter `sort=True` to `utils.update_all_categorized_elements` to be
  able to disable time consuming sorting.
  [gbastien]

0.17 (2017-03-22)
-----------------

- Make the `plone.formwidget.namedfile` `@@download` view can_view aware.
  [gbastien]

0.16 (2017-03-08)
-----------------

- Correctly hide to_print and confidential widgets on add and display view
  if they were deactivated on the group
  [mpeeters]
- Add new events to limit updated informations on parent
  [mpeeters]
- Add an option to update only category informations on parent
  [mpeeters]

0.15 (2017-02-17)
-----------------

- Adapted translations so it is more understandable.
  [gbastien]
- Do only call `_cookCssResources` in `category_before_remove` if not currently
  removing the `Plone Site`.
  [gbastien]
- Make `ICategory.icon` a primary field so we may use a simpler download URL
  that is only the `path_to_object/@@download` without the file name anymore.
  This is done to surround a bug in Apache that occurs when the filename
  contains the `%` character.
  [gbastien]

0.14 (2017-02-13)
-----------------

- Generate a CSS class on the `<ul>` tag of the `categorized-childs-infos` view
  that is the AJAX view called when hovering the `categorized-childs` elements
  that will give the ability to display the infos on several columns.  This is
  necessary when displaying a large amount of categorized elements using same
  content_category.  The `Maximum number of elements to display by columns
  when displaying categorized elements of same category in the tooltipster widget`
  can be defined in the iconifiedcategory control panel.
  [gbastien]
- Moved registry parameter `filesizelimit` to the IIconifiedCategorySettings.
  [gbastien]
- Added a way to defer call to `utils.update_all_categorized_elements` in the
  `categorized_content_container_cloned` IObjectClonedEvent event handler.
  [gbastien]

0.13 (2017-02-09)
-----------------

- Makes `collective-iconifiedcategory.css` cacheable and cookable to avoid
  recomputing it for every pages.  We call `portal_css.cookResources` when
  a category is added or moved.  Not necessary to recook for subcategory
  as it uses same CSS class as parent category.
  [gbastien]

0.12 (2017-02-09)
-----------------

- Do not fail in `utils.get_categorized_elements` if context does not have the
  `categorized_elements` OrderedDict.
  [gbastien]

0.11 (2017-02-07)
-----------------

- Use a batchSize of 999 in the tabview to show every categorized elements.
  [gbastien]
- In `utils.get_categorized_elements`, do not do the catalog query if the
  categorized_elements dict is empty.
  [gbastien]

0.10 (2017-02-05)
-----------------

- Only check `can_view` if current element is `confidential`, moreover only
  instanciate the `IIconifiedContent` adapter to check for `can_view` when
  element is `confidential`.
  [gbastien]

0.9 (2017-01-31)
----------------

- Adapted CSS selector that changes `font-size` of number of categorized
  elements displayed in the tooltipster
  [gbastien]
- Added a way to defer the categorized_content_created event and to defer
  call to utils.update_categorized_elements in the categorized_content_updated
  event.  This way we may manage adding several categorized elements but only
  updating the categorized_elements dict (including time consuming sorting)
  at the right time
  [gbastien]
- Fixed tests to work in both Plone 4.3.7 and Plone 4.3.11
  [gbastien]

0.8 (2017-01-25)
----------------

- Do not fail in `categorized-childs-infos` if current context does not have
  the `categorized_elements` dict
  [gbastien]

0.7 (2017-01-23)
----------------

- Use `category_uid` instead `category_id` as key for infos dict used by
  `CategorizedChildInfosView`, indeed we may have different configurations
  used on same container for different categorized elements and those
  configurations may contain categories with same id
  [gbastien]
- Do not break if icon used for iconified category contains special characters
  [gbastien]

0.6 (2017-01-17)
----------------

- Use ajax to display the categorized childs informations
  [gbastien]
- Display select2 widget larger and with no padding between options
  so more options are displayed together
  [gbastien]
- Added option `show_nothing=True` to the `categorized-childs` view
  to be able to show/hide the 'Nothing' label when there is no categorized
  content to display
  [gbastien]

0.5 (2017-01-13)
----------------

- Do not fail in `utils.sort_categorized_elements` if a key is not found,
  it can be the case when copy/pasting and new element use another
  configuration
  [gbastien]

0.4 (2017-01-12)
----------------

- Sort `categorized_elements` by alphabetical order into a category,
  this way it can be directly displayed as it in the tooltipster
  or in the tabview without having to sort elements again
  [gbastien]
- Add method `IconifiedCategoryGroupAdapter.get_every_categories`
  that gets every available categories.  Mainly made to be overrided,
  it is used in `utils.get_ordered_categories` to manage the fact
  that a container could contain categorized elements using different
  group of categories
  [gbastien]
- Add a configlet to allow user to sort elements on title on the
  categorized tab view
  [mpeeters]
- Ensure that categorized elements are sorted by group folder order
  [mpeeters]
- Refactoring of iconified JavaScript functions
  [mpeeters]
- Increase speed that show the categorized elements in the tooltipster.
  [gbastien]
- Do not fail to remove the Plone Site if categories or subcategorie exist.
  [gbastien]

0.3 (2016-12-21)
----------------

- Changed icon used with link to `More infos`.
  [gbastien]
- Do not fail if subcategory title contains special characters.
  [gbastien]
- Turn icon `more_infos.png` into a separated resource, in addition to other
  resources stored in the `static` folder declared as resourceDirectory,
  so it is easy to override.
  [gbastien]

0.2 (2016-12-07)
----------------

- Use `javascript:event.preventDefault()` when clicking on the tooltipster root
  element to avoid the link action that will change the current url.
  [gbastien]
- Open `More infos` link in `target=_parent` so it opens in the _parent frame
  when displayed in an iframe, namely outside the iframe.
  [gbastien]

0.1 (2016-12-02)
----------------

- Initial release.
  [mpeeters]
