$(function () {
    // 提交表单的事件
    $('form[name="forget-password"]').submit(function (e) {
        e.preventDefault();

        // 避免重复提交过快
        $('#submit-btn').attr('disabled', 'disabled');
        
        // 检查两次密码是否一致
        if ($('form[name="forget-password"] input[name="password"').val() !== $('#again-password').val()) {
            $('#error-modal .modal-body p').text('两次输入的密码不一致！');
            $('#error-modal').modal('show');
            $('#submit-btn').removeAttr('disabled');
            return;
        }

        // 发送表单
        MyGlobalFunction.ajaxPostForm(this, function (data) {
            $('#error-modal .modal-body p').text(data.message);
            $('#error-modal').modal('show');
            
            if (data.status === 1) {
                $('#resend-email')[0].email = $('form[name="forget-password"] input[name="email"]').val();
                $('#resend-email')[0].password = $('form[name="forget-password"] input[name="password"]').val();
                $('#submit-btn').addClass('hidden');
                $('#resend-email').removeClass('hidden');
                MyGlobalFunction.resendButtonCountdownAnimation($('#resend-email')[0], 60);
            }

            $('#submit-btn').removeAttr('disabled');
        });
    });
    
    // 重新发送按钮的点击事件
    $('#resend-email').click(function (e) {
        if (this.email === undefined || this.password === undefined) {
            return;
        }

        // 动画效果
        MyGlobalFunction.resendButtonCountdownAnimation(this, 60);

        // 重发邮件
        MyGlobalFunction.ajaxPostJson('/auth/send_confirm/forget_password', {'email': this.email, 'password': this.password}, function(data) {
            $('#error-modal .modal-body p').text(data.message);
            $('#error-modal').modal('show');
        });
    });
});