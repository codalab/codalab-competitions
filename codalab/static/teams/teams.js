$(document).ready(function() {
    $('.remove-image .btn').click(function() {
        var target = $('#image-clear_id');
        target.prop('checked', true);
        $('.image-removed').css('display', 'block');
        $('.remove-image').css('display', 'none');
        $('.logo-image').css('display', 'none');
    });
});
