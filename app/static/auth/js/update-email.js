$(function () {
    // 提交表单的事件
    $('form[name="update-email"]').submit(function (e) {
        e.preventDefault();

        // 避免重复提交过快
        $('#submit-btn').attr('disabled', 'disabled');

        // 发送表单
        MyGlobalFunction.ajaxPostForm(this, function (data) {
            $('#error-modal .modal-body p').text(data.message);
            $('#error-modal').modal('show');

            if (data.status === 1) {
                $('#resend-email')[0].email = $('form[name="update-email"] input[name="email"]').val();
                $('#submit-btn').addClass('hidden');
                $('#resend-email').removeClass('hidden');
                MyGlobalFunction.resendButtonCountdownAnimation($('#resend-email')[0], 60);
            }

            $('#submit-btn').removeAttr('disabled');
        });
    });

    // 重新发送按钮的点击事件
    $('#resend-email').click(function (e) {
        if (this.email === null) {
            return;
        }

        // 动画效果
        MyGlobalFunction.resendButtonCountdownAnimation(this, 60);

        // 重发邮件
        MyGlobalFunction.ajaxPostJson('/auth/send_confirm/update_email', {'email': this.email}, function(data) {
            $('#error-modal .modal-body p').text(data.message);
            $('#error-modal').modal('show');
        });
    });
});
