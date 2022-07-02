(function () {
    'use strict';

    // 渲染markdown文章
    MyGlobalFunction.marked($('.article-content')[0]);

    // 监听评论表单中的markdown编辑器，并实时渲染
    $('#comment-content').on('input', function () {
        MyGlobalFunction.marked($('form[name="publish-comment"] .markdown-edit-containter')[0]);
    });

    // 发送评论的表单
    $('form[name="publish-comment"]').submit(function (e) {
        e.preventDefault();

        MyGlobalFunction.ajaxPostForm(this, function (data) {
            if (data.status === 1) {
                location.reload();
            } else {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'danger', data.message);
            }
        });
    });

    // 渲染markdown评论
    $.each($('.comment-list .comment-content'), function (i, v) {
        MyGlobalFunction.marked(v);
    });
})();