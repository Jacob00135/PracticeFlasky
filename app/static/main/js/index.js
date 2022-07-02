$(function () {
    // 提交表单
    $('form[name="publish-article"]').submit(function (e) {
        e.preventDefault();

        MyGlobalFunction.ajaxPostForm(this, function (data) {
            if (data.status === 1) {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'success', data.message);
                setTimeout(function () {
                    location.reload();
                }, 3000);
            } else {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'danger', data.message);
            }
        });
    });

    // 监听markdown编辑器，并实时渲染
    $('#article-content').on('input', function () {
        MyGlobalFunction.marked($('form[name="publish-article"] .markdown-edit-containter')[0]);
    });
});