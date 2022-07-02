$(function () {
    const customerName = location.pathname.split('/').pop();

    // 默认的用户身份
    const roleOption = $('#role-name option[selected]')[0];
    if (roleOption !== undefined) {
        roleOption.selected = true;
    }

    // 渲染个人简介
    MyGlobalFunction.ajaxJsonGet('/customer/get_description?customer_name=' + customerName, function (data) {
        if (data.status === 1) {
            $('#description')[0].innerText = data.description;
        }
    });

    // 提交表单事件
    $('#update-info-form').submit(function (e) {
        e.preventDefault();

        // 避免重复提交过快
        $('#submit-btn').attr('disabled', 'disabled');

        // 发送表单
        MyGlobalFunction.ajaxPostForm(this, function (data) {
            if (data.status === 1) {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'success', data.message);
                setTimeout(function () {
                    location.assign('/customer/' + customerName);
                }, 2000);
            } else {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'danger', data.message);
                $('#submit-btn').removeAttr('disabled');
            }
        });
    });
});