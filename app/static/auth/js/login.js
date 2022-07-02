$(function () {
    $('form[name="login"]').attr('action', $('form[name="login"]').attr('action') + '?next=' + (MyGlobalFunction.getQueryParam()['next'] || '/'));

    $('form[name="login"]').submit(function (e) {
        e.preventDefault();

        MyGlobalFunction.ajaxPostForm(this, function (data) {
            if (data.status === 1) {
                location.assign(data['next']);
                return;
            }
            $('#login-error-modal .modal-body p').text(data.message);
            $('#login-error-modal').modal('show');
        });
    });
});