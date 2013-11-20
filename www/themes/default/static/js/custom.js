// customized:

$(function() {

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
    var today = new Date(g_time);
    var this_year = today.getFullYear();
    var now = parseInt(today.getTime() / 1000);
    $('.x-smartdate').each(function() {
        var s = '1分钟前';
        var f = parseInt($(this).attr('date'));
        var t = now - f;
        if (t > 604800) {
            // 1 week ago:
            var that = new Date(f * 1000);
            s = that.getFullYear()==this_year ? (that.getMonth() + 1) + '月' + that.getDate() + '日' : that.getFullYear() + '年' + (that.getMonth() + 1) + '月' + that.getDate() + '日';
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
        $(this).text(s);
    });

    // search query:
    var input_search = $('input.search-query');
    var old_width = input_search.css('width');
    input_search.bind('focusin', function() {
        input_search.animate({'width': '180px'}, 500);
    }).bind('focusout', function() {
        input_search.animate({'width': old_width}, 500);
    });
    // END
});

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
    $('span.x-user-name').text(u.name);
    $('.x-auth-signed').show();
    $('.x-auth-not-signed').hide();
}
