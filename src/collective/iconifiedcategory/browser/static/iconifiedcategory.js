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

  $('a.iconified-action').click(function() {
    var obj = $(this);
    var values = {'iconified-value': !obj.hasClass('active')};
    $.getJSON(
      obj.attr('href'),
      values,
      function(data) {
        obj.toggleClass('active');
      }
    );
    return false;
  });

});
