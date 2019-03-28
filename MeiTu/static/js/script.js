$(function () {
    function render_time() {
        return moment($(this).data('timestamp')).format('lll')
    }

    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    );
});


$(document).ready(function () {
    $.goup({
        trigger: 100,
        bottomOffset: 150,
        locationOffset: 100,
        title: '返回顶部',
        titleAsText: true
    });
});


$('#getCode').unbind('click').click(function (event) {
    event.preventDefault();
    time(this);
    sendEmail()
});
var wait = 60;

function time(o) {
    if (wait == 0) {
        o.removeAttribute("disabled");
        o.innerHTML = "发送验证码";
        wait = 60;
    } else {
        o.setAttribute("disabled", true);
        o.innerHTML = "重新发送(" + wait + ")";
        wait--;
        setTimeout(function () {
            time(o)
        }, 1000)
    }
}

function sendEmail() {
    $.ajax({
        type: 'GET',
        url: '/user/send_verify',
        dataType: 'json',
        success: function (data) {
            if (data.data == 60) {
                alert('发送频率过快，请稍后重试')
            } else {
                alert(data.data)
            }
        },
        error: function () {
            alert('邮件发送失败')
        }
    })
}