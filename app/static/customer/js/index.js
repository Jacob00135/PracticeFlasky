$(function () {
    // 渲染个人简介
    MyGlobalFunction.ajaxJsonGet('/customer/get_description?customer_name=' + $('h1').text(), function (data) {
        if (data.status === 1) {
            $('#desc .panel-body')[0].innerText = data.description;
        }
    });

    // 关注按钮
    $('#follow').click(follow);
    function follow() {
        MyGlobalFunction.ajaxPostJson('/customer/follow', { 'customer-name': $('h1').text() }, function (data) {
            // 显示提示框
            MyGlobalFunction.showSimpleHintModal('hint-modal', data.status === 1 ? 'success' : 'danger', data.message);

            // 把按钮改成“取消关注”
            $('#follow').html('取消关注');
            $('#follow').removeClass('btn-success');
            $('#follow').addClass('btn-danger');
            $('#follow').unbind('click', follow);
            $('#follow').attr('id', 'unfollow');
            $('#unfollow').click(unfollow);
        });
    }

    // 取消关注按钮
    $('#unfollow').click(unfollow);
    function unfollow() {
        MyGlobalFunction.ajaxPostJson('/customer/unfollow', { 'customer-name': $('h1').text() }, function (data) {
            // 显示提示框
            MyGlobalFunction.showSimpleHintModal('hint-modal', data.status === 1 ? 'success' : 'danger', data.message);

            // 把按钮改成“关注”
            $('#unfollow').html('关注');
            $('#unfollow').removeClass('btn-danger');
            $('#unfollow').addClass('btn-success');
            $('#unfollow').unbind('click', unfollow);
            $('#unfollow').attr('id', 'follow');
            $('#follow').click(follow);
        });
    }

    // 更换头像模态框弹出后做的操作
    $('#update-hp-modal').on('show.bs.modal', function () {
        // 显示当前头像
        $('#preview-head-portrait').attr('src', $('#head-portrait').attr('src'));

        // 隐藏警告框
        $('#upload-alert').addClass('hidden');

        // 清空文件列表
        $('#upload-head-portrait').html('<div class="text">上传</div><input type="file" accept="image/png, image/jpeg" />');

        // 绑定上传文件事件
        $('#upload-head-portrait input').on('input', uploadHeadPortrait);

        // 禁用提交按钮
        $('#submit-head-portrait')[0].disabled = true;
    });

    // 点击更改头像模态框中的警告框关闭按钮后，隐藏警告框而不是移除警告框
    $('#upload-alert .close').click(function () {
        $('#upload-alert').addClass('hidden');
    });

    // 上传文件后，检查文件合法性
    // 若不合法，则禁用提交按钮、出现提示框、允许再次上传
    // 若合法，则启用提交按钮、关闭提示框、允许再次上传
    function uploadHeadPortrait (e) {
        const input = e.target;
        if ((input.allowUpload === undefined || input.allowUpload === true) && input.files.length > 0) {
            const img = input.files[0];
            $('#upload-head-portrait .text').text(img.name);
            input.allowUpload = false; // 防止用户点击上传太快

            // 检查图片大小
            if (img.size / 1024 > 100) {
                $('#submit-head-portrait').addClass('disabled');
                $('#upload-alert .content').text('上传的图片必须小于100KB!');
                $('#upload-alert').removeClass('hidden');
                input.allowUpload = true;
                return;
            }

            // 检查图片扩展名
            const extensionName = img.name.split('.').pop();
            const allowExtensionName = ['jpg', 'jpeg', 'png'];
            let allow = false;
            for (let i = 0; i < allowExtensionName.length; i++) {
                if (extensionName === allowExtensionName[i]) {
                    allow = true;
                    break;
                }
            }
            if (!allow) {
                $('#submit-head-portrait').addClass('disabled');
                $('#upload-alert .content').text('上传的图片扩展名必须是' + allowExtensionName.join(',') + '其中一个');
                $('#upload-alert').removeClass('hidden');
                input.allowUpload = true;
                return;
            }

            // 图片合法
            $('#preview-head-portrait').attr('src', URL.createObjectURL(img));
            $('#upload-alert').addClass('hidden');
            URL.revokeObjectURL($('#preview-head-portrait').attr('src'));
            $('#submit-head-portrait').removeClass('disabled');
            input.allowUpload = true;
            $('#submit-head-portrait')[0].disabled = false;
        }
    }

    // 提交上传的头像
    $('#submit-head-portrait').click(function () {
        // 禁止上传头像，关闭更改头像模态框
        this.disabled = true;
        $('#update-hp-modal').modal('hide');
        $('#hint-modal .modal-body').removeClass('bg-success');
        $('#hint-modal .modal-body').removeClass('bg-danger');
        $('#hint-modal .modal-body span.text-danger').addClass('hidden');
        $('#hint-modal .modal-body span.text-success').addClass('hidden');
        $('#hint-modal .modal-body p').removeAttr('class');
        $('#hint-modal .modal-body p').text('正在上传头像，请不要关闭此窗口');
        $('#hint-modal').modal('show');

        // 上传更改后的头像
        const formData = new FormData();
        formData.set('head_portrait', $('#upload-head-portrait input')[0].files[0]);
        MyGlobalFunction.ajaxPostFile('/customer/update_head_portrait/' + $('h1').text(), formData, function (data) {
            if (data.status === 1) {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'success', data.message);
                setTimeout(function () {
                    location.reload();
                }, 2000);
            } else {
                MyGlobalFunction.showSimpleHintModal('hint-modal', 'danger', '上传头像失败，' + data.message);
            }
        });
    })
});

// (function () {
//     'use strict';
//
//     const headPortrait = document.querySelector('.customer-info .head-portrait img');
//     const uploadInput = document.querySelector('.customer-info .upload-group input[type="file"]');
//     const decideGroup = document.querySelector('.customer-info .decide-group');
//     const hintBoxGroup = document.querySelector('.customer-info .hint-box-group');
//     const followButton = document.querySelector('#follow');
//     const unfollowButton = document.querySelector('#unfollow');
//     const srouceImageSrc = headPortrait.src;
//     const allowExtensionName = ['jpg', 'jpeg', 'png'];
//     let allowUpload = true; // 防止用户上传太快
//     let allowFollow = true; // 防止用户点击关注太快
//     let allowUnfollow = true; // 防止用户点击取消关注太快
//
//     // 渲染个人简介
//     const customerName = document.querySelector('h1').innerHTML;
//     ajaxJsonGet('/customer/get_description?customer_name=' + customerName, function (responseJson) {
//         if (responseJson.status === 1) {
//             document.querySelector('.customer-info .description .content').innerText = responseJson['description'];
//         }
//     });
//
//     // 更换头像点击事件
//     if (uploadInput !== null) {
//         uploadInput.addEventListener('input', function (event) {
//             if (allowUpload && uploadInput.files.length > 0) {
//                 allowUpload = false;
//                 const img = this.files[0];
//
//                 // 检查图片大小
//                 if (img.size / 1024 > 100) {
//                     showHintBox(hintBoxGroup, '上传的图片必须小于100KB！', 'error');
//                     allowUpload = true;
//                     return undefined;
//                 }
//
//                 // 检查图片扩展名
//                 const extensionName = img.name.split('.').pop();
//                 let allow = false;
//                 for (let i = 0; i < allowExtensionName.length; i++) {
//                     if (extensionName === allowExtensionName[i]) {
//                         allow = true;
//                         break;
//                     }
//                 }
//                 if (!allow) {
//                     showHintBox(hintBoxGroup, '上传的图片类型必须是image/jpeg或image/png', 'error');
//                     allowUpload = true;
//                     return undefined;
//                 }
//
//                 // 显示图片及决定按钮
//                 headPortrait.src = URL.createObjectURL(img);
//                 URL.revokeObjectURL(headPortrait.src);
//                 decideGroup.classList.remove('hidden');
//
//                 allowUpload = true;
//             }
//         });
//     }
//
//     // “√”和“×”按钮的点击事件
//     if (decideGroup !== null) {
//         const yesButton = decideGroup.querySelector('button.yes');
//         const noButton = decideGroup.querySelector('button.no');
//
//         // “√”按钮的点击事件
//         yesButton.addEventListener('click', function (event) {
//             decideGroup.classList.add('hidden');
//
//             const data = new FormData();
//             data.set('head_portrait', uploadInput.files[0]);
//             ajaxPostFile(
//                 '/customer/update_head_portrait/' + location.pathname.split('/').pop(),
//                 data,
//                 hintBoxGroup,
//                 {
//                     'success': function (responseJson) {
//                         location.reload();
//                     }
//                 }
//             );
//         });
//
//         // “×”按钮的点击事件
//         noButton.addEventListener('click', function (event) {
//             headPortrait.src = srouceImageSrc;
//             decideGroup.classList.add('hidden');
//         })
//     }
//
//     // 关注和取消关注
//     function followEventListener(event) {
//         // 锁定事件源
//         const eventTarget = event.target;
//
//         // 安全性处理
//         if (!allowFollow) {
//             return undefined;
//         }
//         allowFollow = false;
//
//         // 发送请求
//         ajaxJsonPost('/customer/follow', {'customer-name': customerName}, function(responseJson) {
//             if (responseJson.status === 1) {
//                 eventTarget.id = 'unfollow';
//                 eventTarget.innerHTML = '取消关注';
//                 eventTarget.removeEventListener('click', followEventListener);
//                 eventTarget.addEventListener('click', unfollowEventListener);
//             } else {
//                 showHintBox(hintBoxGroup, responseJson.message, 'error');
//             }
//             allowFollow = true;
//         });
//     }
//     function unfollowEventListener(event) {
//         // 锁定事件源
//         const eventTarget = event.target;
//
//         // 安全性处理
//         if (!allowUnfollow) {
//             return undefined;
//         }
//         allowUnfollow = false;
//
//         // 发送请求
//         ajaxJsonPost('/customer/unfollow', {'customer-name': customerName}, function(responseJson) {
//             if (responseJson.status === 1) {
//                 eventTarget.id = 'follow';
//                 eventTarget.innerHTML = '关注';
//                 eventTarget.removeEventListener('click', unfollowEventListener);
//                 eventTarget.addEventListener('click', followEventListener);
//             } else {
//                 showHintBox(hintBoxGroup, responseJson.message, 'error');
//             }
//             allowUnfollow = true;
//         });
//     }
//     if (followButton != null) {
//         followButton.addEventListener('click', followEventListener);
//     }
//     if (unfollowButton != null) {
//         unfollowButton.addEventListener('click', unfollowEventListener);
//     }
// })();
