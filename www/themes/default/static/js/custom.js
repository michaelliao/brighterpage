// customized:

$(function() {
    // set user image:
    $('img.x-user-image').attr('src', g_user_image);

    // active nav bar:
    var xnav = $('meta[property="x-nav"]').attr('content');
    $('#main-nav-bar li a[href="' + xnav + '"]').parent().addClass('active');

    // init scroll:
    var $window = $(window);
    var $header = $('#header');
    var $navbar = $('#navbar');
    var $autodisplay = $('.x-autodisplay');
    $window.scroll(function() {
        if ($window.scrollTop() >= 100) {
            if ( ! $navbar.hasClass('navbar-fixed-top')) {
                $navbar.addClass('navbar-fixed-top');
                $header.css('margin-top', '40px');
                $autodisplay.css('display', '');
            }
        }
        else {
            if ($navbar.hasClass('navbar-fixed-top')) {
                $navbar.removeClass('navbar-fixed-top');
                $header.css('margin-top', '0px');
                $autodisplay.css('display', 'none');
            }
        }

        if ($(window).scrollTop() > 1000) {
            $('div.go-top').show();
        }
        else {
            $('div.go-top').hide();
        }
    });

    // go-top:
    $('div.go-top').click(function() {
        $('html, body').animate({scrollTop: 0}, 1000);
    });

    // smart date:
    $('.x-smartdate').each(function() {
        var f = parseInt($(this).attr('date'));
        $(this).text(to_smart_date(f));
    });

    // search query:
    var input_search = $('input.search-query');
    var old_width = input_search.css('width');
    input_search.bind('focusin', function() {
        input_search.animate({'width': '160px'}, 500);
    }).bind('focusout', function() {
        input_search.animate({'width': old_width}, 500);
    });

    // smart video:
    var bSupportVideo = !!document.createElement('video').canPlayType;
    if (bSupportVideo) {
        var v = document.createElement('video');
        bSupportVideo = v.canPlayType('video/mp4')!='';
    }
    $('div[data-type=video]').each(function() {
        var d = $(this);
        d.addClass('x-video');
        if (! bSupportVideo) {
            d.html('<div style="padding:20px 10px;">您的浏览器不支持播放该MP4视频</div>');
        }
        else {
            var src = d.attr('data-src');
            var w = d.attr('data-width');
            var h = d.attr('data-height');
            d.addClass('x-video-active');
            d.html('<div class="x-video-button"><div class="x-video-play"></div></div>');
            var s = '<video width="' + w + '" height="' + h + '" controls="controls" preload="none" autoplay="autoplay" style="border:solid 1px #ccc"><source src="' + src + '" /></video>'
            d.click(function() {
                d.css('display', 'none');
                d.after(s);
            });
        }
    });

    // END
});

function to_smart_date(f) {
    var today = new Date(g_time);
    var this_year = today.getFullYear();
    var now = parseInt(today.getTime() / 1000);

    var s = '1分钟前';
    var t = now - parseInt(f);
    if (t > 604800) {
        // 1 week ago:
        var that = new Date(f * 1000);
        s = '';
        if (that.getFullYear()!=this_year) {
            s = s + that.getFullYear() + '年';
        }
        s = s + (that.getMonth() + 1) + '月' + that.getDate() + '日 ' + that.getHours() + ':';
        var m = that.getMinutes();
        if (m < 10) {
            s = s + '0';
        }
        s = s + m;
    }
    else if (t >= 86400) {
        // 1-6 days ago:
        s = parseInt(t / 86400) + '天前';
    }
    else if (t >= 3600) {
        // 1-23 hours ago:
        s = parseInt(t / 3600) + '小时前';
    }
    else if (t >= 60) {
        s = parseInt(t / 60) + '分钟前';
    }
    return s;
}

function search(keyword) {
    location.assign('http://www.baidu.com/s?ie=utf-8&wd=' + encodeURIComponent(keyword) + '+site%3A' + location.hostname);
    return false;
}

function is_desktop() {
    var ua = navigator.userAgent.toLowerCase();
    return ua.indexOf('windows nt')>=0 || ua.indexOf('macintosh')>=0;
}

function auth_from(provider) {
    var url = '/auth/from/' + provider;
    if (is_desktop()) {
        var w = window.open(url + '?jscallback=onauthcallback', 'x_auth_window', 'top=200,left=400,width=600,height=380,directories=no,menubar=no,toolbar=no,resizable=no');
    }
    else {
        location.assign(url);
    }
}

function onauthcallback(u) {
    console.log(u);
    $('span.x-user-name').text(u.name);
    $('img.x-user-image').attr('src', u.image_url);
    $('.x-auth-signed').show();
    $('.x-auth-not-signed').hide();
}

// create comment by ajax:

function _set_comment_error($form, s) {
    $form.find('span.x-comment-error').text(s);
}

function _set_comment_posting($btn, posting) {
    var $i = $btn.find('i')
    if (posting) {
        $btn.attr('disabled', 'disabled');
        $i.addClass('x-loading');
    }
    else {
        $btn.removeAttr('disabled');
        $i.removeClass('x-loading');
    }
}

var _comment_template = '<!-- comment template -->' +
    '<div class="x-comment-li">' +
    '    <div class="x-comment-img">' +
    '        <img class="x-user-image-small" />' +
    '    </div>' +
    '    <div class="x-comment-main">' +
    '        <div class="x-comment-prompt">' +
    '            <span class="x-comment-username"></span> <span class="x-comment-date"></span>：' +
    '        </div>' +
    '        <div class="x-comment-content"></div>' +
    '        <div class="x-comment-prompt">' +
    '            <span>' +
    '                <a href="#0" onclick="reply_comment(this)">回复</a>' +
    '                <a href="javascript:delete_comment(\'$_ID\')" class="x-delete-comment" style="display:none">删除</a>' +
    '            </span>' +
    '        </div>' +
    '    </div>' +
    '</div>';

function reply_comment(a) {
    var p = $(a);
    while (! p.hasClass('x-comment-li')) {
        if (p.get(0)===document) {
            return;
        }
        p = p.parent();
    }
    var u = '@' + p.find('.x-comment-username').text();
    var $textarea = $('form.x-comment-form').find('textarea[name=content]');
    $textarea.val(u + '\n' + $textarea.val());
    $('html, body').animate({scrollTop: $('form.x-comment-form').position().top - 20});
    $textarea.focus();
    $textarea.get(0).setSelectionRange(u.length + 1, u.length + 1);
}

function _format_lines(s) {
    var ss = s.split('\n');
    var L = [];
    $.each(ss, function(index, value) {
        var l = $.trim(value);
        if (l.length>0) {
            L.push('<p>' + $('<p/>').text(l).html() + '</p>');
        }
    });
    return L.join('');
}

function _add_comment(c) {
    var $dom = $(_comment_template.replace('$_ID', c._id));
    $dom.find('span.x-comment-username').text(c.user_name);
    $dom.find('span.x-comment-date').text(c.creation_time);
    $dom.find('div.x-comment-img img').attr('src', c.user_image_url);
    $dom.find('div.x-comment-content').html(_format_lines(c.content));
    return $dom;
}

function create_comment(form) {
    try {
        var $form = $(form);
        var $btn = $form.find('button[type=submit]');
        var $textarea = $form.find('textarea[name=content]');
        var s = $textarea.val();
        if ($.trim(s).length==0) {
            _set_comment_error($form, '请输入评论内容！');
            return false;
        }

        _set_comment_error($form, '');
        _set_comment_posting($btn, true);

        $.postJSON($form.attr('action'), $form.serialize(), function(result) {
            $textarea.val('');
            result.creation_time = '1分钟前';
            var $dom = _add_comment(result);
            $dom.css('display', 'none');
            $('div.x-comments-list').prepend($dom);
            $dom.slideDown();
        }, function(e) {
            _set_comment_error($form, e.message || e.error);
        }, function() {
            _set_comment_posting($btn, false);
        });
    }
    catch (e) {}
    return false;
}

function delete_comment(cid) {
    if (confirm('delete this comment?')) {
        $.postJSON('/api/comments/' + cid + '/delete', '', function(result) {
            location.reload();
        }, function(e) {
            alert('Error: ' + (e.message || e.error));
        });
    }
}




