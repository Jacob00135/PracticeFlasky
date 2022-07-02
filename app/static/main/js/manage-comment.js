$(function () {
    // 渲染评论中的Markdown文本
    $.each($('.comment-list .comment-content'), function (i, v) {
        MyGlobalFunction.marked(v);
    });

    // 绑定“禁用”“取消禁用”按钮点击事件
    $.each($('.comment-list > li.list-group-item'), function (i, v) {
        const disabledBtn = v.querySelector('.disabled-comment');
        const useBtn = v.querySelector('.use-comment');
        const disabledWarning = v.querySelector('.disabled-warning');
        const commentId = v.getAttribute('data-comment-index');

        // 绑定“禁用”按钮点击事件
        disabledBtn.addEventListener('click', function () {
            MyGlobalFunction.ajaxPostJson('/update_comment_disabled', {'comment_id': commentId, 'disabled': 1}, function (data) {
                if (data.status === 1) {
                    disabledBtn.classList.add('hidden');
                    useBtn.classList.remove('hidden');
                    disabledWarning.classList.remove('hidden');
                } else {
                    MyGlobalFunction.showSimpleHintModal('hint-modal', 'danger', data.message);
                }
            });
        });

        // 绑定“取消禁用“按钮点击事件
        useBtn.addEventListener('click', function () {
            MyGlobalFunction.ajaxPostJson('/update_comment_disabled', {'comment_id': commentId, 'disabled': 0}, function (data) {
                if (data.status === 1) {
                    useBtn.classList.add('hidden');
                    disabledBtn.classList.remove('hidden');
                    disabledWarning.classList.add('hidden');
                } else {
                    MyGlobalFunction.showSimpleHintModal('hint-modal', 'danger', data.message);
                }
            });
        });
    });
});