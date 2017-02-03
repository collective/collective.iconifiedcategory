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
    theme: 'tooltipster-shadow',
    position: 'bottom',
    speed: 100,
    delay: 0,
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

function categorizedChildsInfos() {
    jQuery(function($){

    $('.tooltipster-childs-infos').tooltipster({

        contentAsHTML: true,
        interactive: true,
        theme: 'tooltipster-shadow',
        position: 'bottom',
        speed: 100,
        delay: 50,
        animation: 'fade',
        trigger: 'hover',

        functionBefore: function (origin, helper) {
            helper();
            if (origin.data('loaded') !== true) {
                var category_uid = $(origin).attr('data-category_uid');
                var base_url = $(origin).attr('data-base_url');
                $.ajax({
                    type: 'GET',
                    url: base_url + '/@@categorized-childs-infos',
                    data: {
                        category_uid: category_uid,
                        ajax_load: new Date().getTime(),
                    },
                    success: function (data) {
                        origin.tooltipster('update', data).data('ajax ', 'cached');
                        origin.data('loaded', true);
                        helper();
                    }
                });
            }
        }
    });
})
};

jQuery(document).ready(initializeIconifiedCategoryWidget);
jQuery(document).ready(initializeIconifiedActions);
jQuery(document).ready(categorizedChildsInfos);
