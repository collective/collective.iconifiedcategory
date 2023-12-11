Changelog
=========

0.62 (2023-12-11)
-----------------

- Fixed `CategorizedObjectPreviewAdapter.status` when an existing element is updated.
  [gbastien]

0.61 (2023-11-27)
-----------------

- Simplified `CategorizedChildView.has_elements_to_show`.
  [gbastien]

0.60 (2023-09-21)
-----------------

- Fixed version (2105) in `metadata.xml`.
  [gbastien]

0.59 (2023-09-04)
-----------------

- Display the document conversion spinner in any relevant case.
  [gbastien]
- Added `contentType` value to the `categorized_elements` data.
  [gbastien]

0.58 (2023-08-24)
-----------------

- Added new field `ICategorize.show_preview` to turn link to element to a
  `collective.documentviewer` preview instead download.
  Fixed icon displayed when preview computation in progress.
  [gbastien]
- Force icon `width/height` to `16px` in `tooltipster`
  (`categorized-childs.pt` and `categorized-childs-infos.pt`).
  [gbastien]
- Fixed `ContentCategory` portal_type title in `ContentCategory.xml`.
  [gbastien]

0.57 (2023-03-30)
-----------------

- When no request (when using `plone.app.async`), pass `None` instead `{}`
  to `ImageDataModifiedImageScaling` so `plone.namedfile` scaling is happy
  when using `plone.protect >= 3`.
  [aduchene]

0.56 (2023-02-27)
-----------------

- Adapted french translation for `More infos`.
  [gbastien]

0.55 (2022-09-29)
-----------------

- Fixed `utils.get_ordered_categories` and
  `IconifiedCategoryGroupAdapter.get_every_categories` to make sure returned
  categories are from the correct `config_root` and `cachekey` is invalidated
  if `config_root` changed.
  [gbastien]

0.54 (2022-06-14)
-----------------

- Added `@@categorized-childs-manage` that will render a link to manage
  categorized elements.
  [gbastien]
- Implemented `CategorizedContent._unrestrictedGetObject` as `collective.eeafaceted.z3ctable`
  calls now `item._unrestrictedGetObject` instead `item.getObject` for performance optimization.
  [gbastien]
- Added `safe_utils.py` that will only include safe utils.
  [gbastien]
- We need to escape some content to avoid malicious content:

  - Rely on collective.eeafaceted.z3ctable to display the categorized content table, it manages escaping content;
  - Escape category title in vocabularies.

  [gbastien]

0.53 (2022-04-22)
-----------------

- Make `validateFileIsPDF` invariant check if a `contentType` is directly
  available on data, this avoid checking on the file.
  [gbastien]

0.52 (2022-03-22)
-----------------

- Fixed `metadata.xml` version, set `2103` instead `2101`.
  [gbastien]

0.51 (2022-03-10)
-----------------

- Updated upgrade step to 2103 (`Add 'last_updated' to categorized_elements`),
  do not stop in case we found a `last_updated` key in `categorized_elements`
  of an element but continue to next element, maybe some elements were updated
  by another part of code.
  [gbastien]

0.50 (2022-01-03)
-----------------

- Use unrestricted catalog query when possible.
  [gbastien]
- For the view that generated the CSS, do the catalog query that gets the categories
  without `path` and `sort_on` as called from portal and order does not matter.
  [gbastien]
- Added `collective.iconifiedcategory.every_categories` and
  `collective.iconifiedcategory.every_category_titles` vocabularies returning
  every possible categories, including not enabled ones. This will be used to
  manage a `MissingTerms` adapter for `z3c.form`.
  [gbastien]
- Fixed view that generates `collective-iconifiedcategory.css`, get every
  categories including ones that are not `enabled`.
  [gbastien]
- Optimized `@@categorized-childs` view, compute everything only one time
  (context url, context UID, ...) and use `python` or `string` in TAL expressions.
  By default call `utils.get_categorized_elements` with `check_can_view=False`.
  [gbastien]
- Added `check_can_view=True` parameter to `utils.get_categorized_elements`.
  This will do the `IIconifiedContent.can_view` check only done when necessary.
  [gbastien]
- Added data `last_updated` to `categorized_elements` to be used for caching.
  Added upgrade step to version `2103`.
  [gbastien]
- Optimized `ram.cache` key for `utils.get_ordered_categories`, cache until
  any category added/deleted/position changed.
  [gbastien]

0.49 (2021-07-16)
-----------------

- Added possibility to filter displayed categorized elements on any attribute
  of the categorized element.
  [gbastien]
- Rely on imio.helpers because we need the `:json` suffix type converter.
  [gbastien]
- Register the `categorized_content_container_cloned ObjectClonedEvent` handler
  only for `AT IBaseObject` and `DX IDexterityContent` or is is applied also
  for other elements like `portal_type` because it provides `OFS IItem`.
  [gbastien]
- Added specific `collective.iconifiedcategory.belowcategorizedelements` viewlet
  manager just under the categorized elements table that will be displayed if
  table displayed.
  [gbastien]
- Make the `z3c.table CategorizedTable` easy to override by making a
  `BrowserView` out of it.
  [gbastien]
- Adapted `FilesizeColumn` to display total filesize in column header.
  [gbastien]
- Added `soft_warn_filesize`, a CSS class applied to files of more that `1 Mb`
  (like it is already the case for the `warn_filesize` CSS class applied to
  files of more than `5 Mb`).
  [gbastien]
- Removed the `Show details` action, details are always shown, except, for
  display reasons, when more that 2 columns of elements in the popup.
  [gbastien]

0.48 (2021-01-19)
-----------------

- Rely on `CategorizedObjectAdapter.can_view` to manage access to a categorized
  element, this way, we may manage usecases where current user does not have
  the `View` permission on the element but access is managed by the `can_view`
  adapter method.
  [gbastien]

0.47 (2020-08-18)
-----------------

- Added missing translation for `Nothing.`.
  [gbastien]
- In `utils._categorized_elements`, use `aq_base` to get `categorized_elements`
  to be sure we get the one on context.
  Indeed the parent could have this attribute too...
  [gbastien]
- Do not use `portal_catalog` to get `categorized_elements`, instead, store
  `allowedRolesAndUsers` in the `categorized_elements` data and rely on it to
  get the content directly stored in the parent.  This for performance reasons.
  [gbastien]
- Remove unused `utils.get_UID` function.
  [gbastien]
- Make sure a content created with an unexisting `content_category`
  does not break anything.
  [gbastien]

0.46 (2020-06-24)
-----------------

- Make `plone.restapi` validation happy by defining default value for
  `IIconifiedCategorization.default_titles` that is not stored on the
  adapted context.
  [gbastien]

0.45 (2020-05-26)
-----------------

- When using `collective.solr`, brains are not `ICatalogBrain` but `PloneFlare`
  so register `IIconifiedContent` adapter for it when installed.
  [gbastien]

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
