Changelog
=========

0.3 (unreleased)
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
