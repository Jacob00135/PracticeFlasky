(function () {
    'use strict';

    // 进入页面后，渲染表单中的Markdown文本
    MyGlobalFunction.marked($('form[name="edit-article"] .markdown-edit-containter')[0]);

    // 监听表单中的Markdown文本，并实时渲染
    $('#article-content').on('input', function () {
        MyGlobalFunction.marked($('form[name="edit-article"] .markdown-edit-containter')[0]);
    });

    // 发送表单
    $('form[name="edit-article"]').submit(function (e) {
        e.preventDefault();

        MyGlobalFunction.ajaxPostForm(this, function (data) {
            if (data.status === 1) {
                location.assign(data['next']);
            } else {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'danger', data.message);
            }
        });
    });
})();