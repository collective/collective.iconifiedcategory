initializeIconifiedCategoryWidget = function () {

jQuery(function($) {

  var category_selector = '#form_widgets_IIconifiedCategorization_content_category';

  var define_default_title = function(select) {
    var obj = $('#' + select.val());
    /* title field id depends on used behavior (basic, dublincore, ...)
       so we get the id beginning with 'form-widgets-' and ending with '-title' */
    $('input#[id^=form-widgets-][id$=-title]').val(obj.val());
  };

  $(category_selector).change(function() {
    define_default_title($(this));
  });
  define_default_title($(category_selector));

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
    if (obj.hasClass('deactivated')) {
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
