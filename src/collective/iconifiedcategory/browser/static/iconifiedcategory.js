jQuery(document).ready(function($) {

  $('#form_widgets_IIconifiedCategorization_content_category').change(function() {
    obj = $('#' + $(this).val());
    $('#form-widgets-IDublinCore-title').val(obj.val());
  });

});
