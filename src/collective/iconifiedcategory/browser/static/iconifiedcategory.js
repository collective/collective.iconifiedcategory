var IconifiedCategory = {};

IconifiedCategory.defineDefaultTitle = function(select, init_time=false) {
  var container = select.closest('form');
  var obj = $('#' + select.val());
  if (!obj.length) {
    return false;
  }
  /* title field id depends on used behavior (basic, dublincore, ...)
     so we get the id beginning with 'form-widgets-' and ending with '-title' */
  var field = container.find('input#[id^=form-widgets-][id$=-title]');
  if (init_time && field.val()) {
    return
  }
  field.val(obj.val());
};

IconifiedCategory.initializeCategoryWidget = function(obj) {
  obj.change(function() {
    IconifiedCategory.defineDefaultTitle($(this));
  });
  IconifiedCategory.defineDefaultTitle(obj, init_time=true);
}

initializeIconifiedCategoryWidget = function () {

jQuery(function($) {

  IconifiedCategory.initializeCategoryWidget($('#form_widgets_IIconifiedCategorization_content_category'));

  $('.tooltip').tooltipster({
    functionInit: function(origin, content) {
      var id = $(origin).attr('href');
      return $(id).html();
    },
    contentAsHTML: true,
    interactive: true,
    position: 'top-left',
    theme: 'tooltipster-shadow',
    position: 'bottom',
    speed: 200,
    delay: 50,
    animation: 'fade'
    });

});

};

initializeIconifiedActions = function () {

jQuery(function($) {

  $('a.deactivated').click(function() {
    return false;
  });

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
        if (data['status'] == 0) {
          obj.toggleClass('active');
          obj.removeClass('error');
        } else {
          obj.addClass('error');
        }
        obj.attr('alt', data['msg']);
        obj.attr('title', data['msg']);
      }
    );
    return false;
  });

});

};

jQuery(document).ready(initializeIconifiedCategoryWidget);
jQuery(document).ready(initializeIconifiedActions);
