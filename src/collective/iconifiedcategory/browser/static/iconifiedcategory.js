jQuery(document).ready(function($) {

  $('#form_widgets_IIconifiedCategorization_content_category').change(function() {
    var obj = $('#' + $(this).val());
    $('#form-widgets-IDublinCore-title').val(obj.val());
  });

  $('a.deactivated').click(function() {
    return false;
  });

  $('.tooltip').tooltipster({
    functionInit: function(origin, content) {
      var id = $(origin).attr('href');
      return $(id).html();
    },
    contentAsHTML: true,
    interactive: true,
    position: 'top-left',
    theme: 'tooltipster-light',
  });

  var execute_action = function(obj, href, values) {
    if (obj.hasClass('deactivated')) {
      return false;
    }
    $.getJSON(
      href,
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
  }

  var ajax_submit = function(event) {
    var form = $(event.currentTarget).closest('form');
    var input_types = ['select', 'input'];
    var values = {};
    for (var i = 0; i < input_types.length; i++ ) {
      form.find(input_types[i]).each(function() {
        var element = $(this);
        values[element.attr('name')] = element.val();
      });
    }
    console.log(values);
    return false;
  }

  $('td.iconified-custom-confidential a.iconified-action').click(function(event) {
    var obj = $(this);
    if (obj.hasClass('active')) {
      return true;
    }
    event.stopPropagation();
    var container = $(this).closest('td');
    var dialog = $('<div id="dialog" style="display:none;"></div>');
    container.append(dialog);
    dialog.load(
      obj.attr('href') + ' div#confidential-form',
      function(response, status, xhr) {
        dialog.dialog();
        console.log(dialog.find('input[type="submit"]'));
        dialog.find('input[type="submit"]').click(ajax_submit);
      }
    );
    return false;
  });

  $('a.iconified-action').click(function(event) {
    if (event.isPropagationStopped()) {
      return false;
    }
    var obj = $(this);
    var values = {'iconified-value': !obj.hasClass('active')};
    return execute_action(obj, obj.attr('href'), values);
  });

});
