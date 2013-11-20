function refresh() {
    location.assign('?t=' + new Date().getTime());
}

function show_error(err, field_name) {
    $('div.control-group').removeClass('error');
    if (err) {
        $('.alert-error').text(err).show();
        try {
            if ($('.alert-error').offset().top < ($(window).scrollTop() - 41)) {
                $('html,body').animate({scrollTop: $('.alert-error').offset().top - 41});
            }
        }
        catch (e) {}
    }
    else {
        $('div.alert-error').text('').hide();
        return false;
    }
    if (field_name) {
        $('.field-' + field_name).addClass('error');
    }
    return false;
}

function show_loading(show) {
    if (show) {
        $('button[type=submit]').attr('disabled', 'disabled');
        $('button[type=submit] > i').addClass('loading');
    }
    else {
        $('button[type=submit]').removeAttr('disabled');
        $('button[type=submit] > i').removeClass('loading');
    }
}

function show_success() {
    $('.alert-success').show().delay(3000).slideUp(300);
    if ($('.alert-success').offset().top < $(window).scrollTop()) {
        $('html,body').animate({scrollTop: $('.alert-success').offset().top});
    }
}

function show_confirm(title, text_or_html, fn_ok, fn_cancel) {
    var s = '<div class="modal hide fade"><div class="modal-header"><button type="button" class="close" data-dismiss="modal">&times;</button>'
          + '<h3>' + $('<div/>').text(title).html() + '</h3></div>'
          + '<div class="modal-body">'
          + ((text_or_html.length > 0 && text_or_html[0]=='<') ? text_or_html : '<p>' + $('<div/>').text(text_or_html).html() + '</p>')
          + '</div><div class="modal-footer"><a href="#" class="btn btn-primary"><i class="icon-ok icon-white"></i> OK</a><a href="#" class="btn" data-dismiss="modal"><i class="icon-remove"></i> Cancel</a></div></div>';
    $('body').prepend(s);
    var $modal = $('body').children(':first');
    $modal.modal('show');
    $modal.find('.btn-primary').click(function() {
        $modal.attr('result', 'ok');
        $(this).attr('disabled', 'disabled');
        $(this).find('i').addClass('loading');
        fn_ok && fn_ok($(this), function() {
            $modal.modal('hide');
        });
    });
    $modal.on('hidden', function() {
        $modal.remove();
        if ($modal.attr('result')=='ok')
            fn_cancel && fn_cancel();
    });
}

function filesize(size) {
    if (size < 1024)
        return size + ' bytes';
    size = size / 1024.0;
    if (size < 1024)
        return size.toFixed(2) + ' KB';
    size = size / 1024.0;
    if (size < 1024)
        return size.toFixed(2) + ' MB';
    size = size / 1024.0;
    return size.toFixed(2) + ' GB';
}

function getObjectURL(file) {
    var url = '';
    if (window.createObjectURL!=undefined) // basic
        url = window.createObjectURL(file);
    else if (window.URL!=undefined) // mozilla(firefox)
        url = window.URL.createObjectURL(file);
    else if (window.webkitURL!=undefined) // webkit or chrome
        url = window.webkitURL.createObjectURL(file);
    return url;
}

$(function() {
    $('a[data-toggle=tooltip]').tooltip();
    $('#top-nav li').each(function(e) {
        if (location.pathname.indexOf($(this).find('a').attr('href'))==0) {
            $(this).addClass('active');
        }
    });
});
