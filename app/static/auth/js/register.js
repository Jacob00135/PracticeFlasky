$(function () {
    // 提交表单的事件
    $('form[name="register"]').submit(function (e) {
        e.preventDefault();

        // 避免重复提交过快
        $('#register-btn').attr('disabled', 'disabled');
        
        // 检查两次密码是否一致
        if ($('form[name="register"] input[name="password"').val() !== $('#again-password').val()) {
            $('#error-modal .modal-body p').text('两次输入的密码不一致！');
            $('#error-modal').modal('show');
            $('#register-btn').removeAttr('disabled');
            return;
        }

        // 发送表单
        MyGlobalFunction.ajaxPostForm(this, function (data) {
            $('#error-modal .modal-body p').text(data.message);
            $('#error-modal').modal('show');
            
            if (data.status === 1) {
                $('#resend-email')[0].email = $('form[name="register"] input[name="email"]').val();
                $('#register-btn').addClass('hidden');
                $('#resend-email').removeClass('hidden');
                MyGlobalFunction.resendButtonCountdownAnimation($('#resend-email')[0], 60);
            }

            $('#register-btn').removeAttr('disabled');
        });
    });
    
    // 重新发送按钮的点击事件
    $('#resend-email').click(function (e) {
        if (this.email === null || this.email === undefined) {
            return;
        }

        // 动画效果
        MyGlobalFunction.resendButtonCountdownAnimation(this, 60);

        // 重发邮件
        MyGlobalFunction.ajaxPostJson('/auth/send_confirm/register', {'email': this.email}, function(data) {
            $('#error-modal .modal-body p').text(data.message);
            $('#error-modal').modal('show');
        });
    });
});