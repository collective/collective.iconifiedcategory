var IconifiedCategory = {};

IconifiedCategory.defineDefaultTitle = function(select, init_time=false) {
  var container = select.closest('form');
  var obj = $('#' + select.val());
  if (!obj.length) {
    return false;
  }
  /* title field id depends on used behavior (basic, dublincore, ...)
     so we get the id beginning with 'form-widgets-' and ending with '-title' */
  var field = container.find("input[id^='form-widgets-'][id$='-title']");
  if (init_time && field.val()) {
    return;
  }
  field.val(obj.val());
};

IconifiedCategory.initializeCategoryWidget = function(obj) {
  obj.change(function() {
    IconifiedCategory.defineDefaultTitle($(this));
  });
  IconifiedCategory.defineDefaultTitle(obj, init_time=true);
};

/* css classes of a category option: the icon of the category (@@collective-iconifiedcategory.css),
   "subcategory" indents a subcategory, shown with the icon of its category */
IconifiedCategory.categoryCss = function(value) {
  var parts = value.split('_-_');
  return (parts.length > 3 ? 'subcategory ' : '') + parts.slice(0, 3).join('-');
};

/* option titles are already HTML-escaped by the vocabulary */
IconifiedCategory.formatCategory = function(state) {
  if (!state.id) {
    return state.text;
  }
  return '<span class="' + IconifiedCategory.categoryCss(state.id) + '">' + state.text + '</span>';
};

/* show the category icons in the pat-select2 widget (select2 3.5) */
IconifiedCategory.showCategoryIcons = function(select) {
  var select2 = select.data('select2');
  if (!select2) {
    return;
  }
  select2.opts.formatResult = IconifiedCategory.formatCategory;
  select2.opts.formatSelection = IconifiedCategory.formatCategory;
  select2.updateSelection(select2.data());
};

initializeIconifiedCategoryWidget = function () {
  jQuery(function($) {
    var select = $('#form-widgets-IIconifiedCategorization-content_category');
    IconifiedCategory.initializeCategoryWidget(select);
    // pat-select2 is initialized asynchronously, maybe already done
    IconifiedCategory.showCategoryIcons(select);
    select.on('init.select2.patterns', function() {
      IconifiedCategory.showCategoryIcons(select);
    });
  });
};

initializeIconifiedActions = function () {

jQuery(function($) {

  //$('a.deactivated').click(function() {
  //  return false;
  //});

  $('a.iconified-action').click(function() {
    var obj = $(this);
    if (!obj.hasClass('editable')) {
      return false;
    }
    var values = {'iconified-value': !obj.hasClass('active')};
    $.getJSON(
      obj.attr('href'),
      values,
      function(data) {
        if (data.reload) {
          window.location.reload();
          return;
        }
        if (data.status == 0) {
          obj.removeClass('active');
          obj.removeClass('deactivated');
          obj.removeClass('error');
        } else if (data.status == 1) {
          obj.addClass('active');
          obj.removeClass('deactivated');
          obj.removeClass('error');
        } else if (data.status == -1) {
          obj.removeClass('active');
          obj.addClass('deactivated');
          obj.removeClass('error');
        } else {
          obj.addClass('error');
          }
        obj.attr('alt', data.msg);
        obj.attr('title', data.msg);
      }
    );
    return false;
  });

});

};

function categorizedChildsInfos(options={}) {
    selector = options.selector || '.tooltipster-childs-infos';
    tooltipster_helper(selector=selector,
                       view_name='@@categorized-childs-infos',
                       data_parameters=['category_uid', 'filters:json']);

}

jQuery(document).ready(initializeIconifiedCategoryWidget);
jQuery(document).ready(initializeIconifiedActions);
jQuery(document).ready(categorizedChildsInfos);
