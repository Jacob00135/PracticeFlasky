window.MyGlobalFunction = {
    'ajaxJsonGet': function (url, callback) {
        $.ajax({
            'type': 'GET',
            'url': url,
            'contentType': 'application/json',
            'dataType': 'json',
            'success': callback
        });
    },

    'ajaxPostJson': function (url, data, callback) {
        $.ajax({
            'type': 'POST',
            'url': url,
            'contentType': 'application/json',
            'data': JSON.stringify(data),
            'dataType': 'json',
            'success': callback
        });
    },

    'ajaxPostForm': function (form, callback) {
        // 使用ajax代替表单发送数据

        const sendData = {};
        $.each($(form).serializeArray(), function (i, v) {
            sendData[v.name] = v.value;
        });
        $.ajax({
            'type': 'POST',
            'url': form.action,
            'contentType': 'application/json',
            'data': JSON.stringify(sendData),
            'dataType': 'json',
            'success': callback
        });
    },

    'ajaxPostFile': function (url, formData, callback) {
        const xhr = new XMLHttpRequest();
        xhr.open('post', url, true);
        xhr.send(formData);
        xhr.addEventListener('readystatechange', function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                callback(JSON.parse(xhr.responseText));
            }
        });
    },

    'getQueryParam': function () {
        const data = {};
        if (location.search !== '') {
            const itemArr = location.search.split('?').pop().split('&');
            for (let i = 0; i < itemArr.length; i++) {
                let item = itemArr[i];
                let key = item.split('=', 1)[0];
                let value = item.slice(key.length + 1);
                data[key] = value;
            }
        }
        return data;
    },

    'resendButtonCountdownAnimation': function (obj, countdownTime) {
        // 重新发送按钮的倒计时动画，obj是按钮对象，countdownTime是倒计时时间（秒）

        obj.setAttribute('disabled', 'disabled');
        obj.countdownAnimation = setInterval(function () {
            if (countdownTime <= 0) {
                clearInterval(obj.countdownAnimation);
                obj.innerHTML = '重新发送';
                obj.removeAttribute('disabled');
            } else {
                countdownTime = countdownTime - 1;
                obj.innerHTML = '重新发送(' + countdownTime + 's)';
            }
        }, 1000);
    },

    'showSimpleHintModal': function (modalId, level, message) {
        /**
         * @function 弹出提示模态框
         * @param modalId {String} 模态框的Id字符串
         * @param level {String} 提示级别，可取'success', 'danger'
         * @param message {String} 提示消息
         */

        // 检查参数
        if (level !== 'success' && level !== 'danger') {
            throw 'level的值只能取"success"、"danger"的其中一个！';
        }

        // 获取元素
        const modal = $('#' + modalId);
        const body = $('#' + modalId + ' .modal-body');
        const p = $('#' + modalId + ' .modal-body p');
        const textDanger = $('#' + modalId + ' .modal-body span.text-danger');
        const textSuccess = $('#' + modalId + ' .modal-body span.text-success');

        // 操作模态框
        if (level === 'success') {
            body.removeClass('bg-danger');
            body.addClass('bg-success');
            p.attr('class', 'text-success');
            textDanger.addClass('hidden');
            textSuccess.removeClass('hidden');
        } else {
            body.removeClass('bg-success');
            body.addClass('bg-danger');
            p.attr('class', 'text-danger');
            textSuccess.addClass('hidden');
            textDanger.removeClass('hidden');
        }
        p.text(message);
        modal.modal('show');
    }
}


// function ajax(method, url, headers, data, callback) {
//     method = method.toLowerCase();
//     if (method !== 'get' && method !== 'post') {
//         throw Error('请求方式只能是get和post!');
//     }

//     const xhr = new XMLHttpRequest();
//     xhr.open(method, url, true);
//     for (let key in headers) {
//         xhr.setRequestHeader(key, headers[key]);
//     }

//     if (method === 'post') {
//         xhr.send(data);
//     } else {
//         xhr.send();
//     }
//     if (callback) {
//         xhr.addEventListener('readystatechange', function () {
//             if (xhr.readyState === 4 && xhr.status === 200) {
//                 callback(xhr.responseText);
//             }
//         });
//     }
// }

// function ajaxJsonGet(url, callback) {
//     const xhr = new XMLHttpRequest();
//     xhr.open('get', url, true);
//     xhr.send();
//     xhr.addEventListener('readystatechange', function () {
//         if (xhr.readyState === 4 && xhr.status === 200) {
//             callback(JSON.parse(xhr.responseText));
//         }
//     });
// }

// function ajaxJsonPost(url, data, callback) {
//     const xhr = new XMLHttpRequest();
//     xhr.open('post', url, true);
//     xhr.setRequestHeader('Content-Type', 'application/json');
//     xhr.send(JSON.stringify(data));
//     xhr.addEventListener('readystatechange', function () {
//         if (xhr.readyState === 4 && xhr.status === 200) {
//             callback(JSON.parse(xhr.responseText));
//         }
//     });
// }

// function valueInArray(array, value) {
//     for (let i = 0; i < array.length; i++) {
//         if (array[i] === value) {
//             return true;
//         }
//     }
//     return false;
// }

// function getCutString(content) {
//     // 截取200个长度的字符，中文字符长度记为2，非中文字符长度记为1
//     let length = 0;
//     let ls = []
//     for (let i = 0; i < content.length; i++) {
//         let s = content.charAt(i);
//         if (/[\u4e00-\u9fa5]/.test(s)) {
//             length = length + 2;
//         } else {
//             length = length + 1;
//         }
//         if (length >= 200) {
//             ls.push('...');
//             break;
//         }
//         ls.push(s);
//     }
//     return ls.join('');
// }

// function setImageSrc(imageNode, imageName) {
//     // 请求图片的base64码，并设置为指定的图片src
//     ajaxJsonGet('/api/get_head_portrait_base64?filename=' + imageName, function (responseJson) {
//         if (responseJson.status === 1) {
//             imageNode.src = responseJson['result'];
//         }
//     });
// }

// function showHintBox(hintBoxGroup, message, level) {
//     // 显示警示框，必须配合form-module.html中的“.hint-box-group”组件使用
//     hintBoxGroup.classList.add('hidden');
//     const box = hintBoxGroup.querySelector('div');
//     box.innerHTML = message;
//     box.className = level;
//     setTimeout(function () {
//         hintBoxGroup.classList.remove('hidden');
//     }, 100);
// }

// function ajaxPostAndHint(url, data, hintBoxGroup) {
//     ajaxJsonPost(url, data, function (responseJson) {
//         const level = responseJson.status === 1 ? 'hint' : 'error';
//         showHintBox(hintBoxGroup, responseJson.message, level);
//     });
// }

// function ajaxPostFile(url, form, hintBoxGroup, callbackObject) {
//     const xhr = new XMLHttpRequest();
//     xhr.open('post', url, true);
//     xhr.send(form);
//     xhr.addEventListener('readystatechange', function () {
//         if (xhr.readyState === 4 && xhr.status === 200) {
//             const responseJson = JSON.parse(xhr.responseText);
//             if (responseJson.status === 1) {
//                 showHintBox(hintBoxGroup, responseJson.message, 'hint');
//                 if (callbackObject['success'] !== undefined) {
//                     callbackObject['success'](responseJson);
//                 }
//             } else {
//                 showHintBox(hintBoxGroup, responseJson.message, 'error');
//                 if (callbackObject['lose'] !== undefined) {
//                     callbackObject['lose'](responseJson);
//                 }
//             }
//         }
//     });
// }

// function getQueryParam() {
//     const data = {};
//     if (location.search !== '') {
//         const itemArr = location.search.split('?').pop().split('&');
//         for (let i = 0; i < itemArr.length; i++) {
//             let item = itemArr[i];
//             let key = item.split('=', 1)[0];
//             let value = item.slice(key.length + 1);
//             data[key] = value;
//         }
//     }
//     return data;
// }

// function getFullUrl(baseUrl, queryParam) {
//     if (Object.keys(queryParam).length > 0) {
//         const paramArr = [];
//         for (let key in queryParam) {
//             let value = queryParam[key];
//             paramArr.push([key, value].join('='));
//         }
//         return [baseUrl, '?', paramArr.join('&')].join('');
//     }
//     return baseUrl;
// }

// function fillPageListGroup(pageListGroup, nowPage, pageCount) {
//     /**
//      * 渲染页码导航
//      * @pageListGroup 页码导航元素
//      * @nowPage 当前页码
//      * @pageCount 总页码
//      */
//     nowPage = Number(nowPage);
//     pageCount = Number(pageCount);
//     const pageList = pageListGroup.querySelector('.page-list');
//     const pageInfo = pageListGroup.querySelector('.page-info');
//     const firstDiv = pageList.querySelector('div:first-of-type');
//     const prevDiv = pageList.querySelector('.prev');
//     const nowDiv = pageList.querySelector('.now');
//     const nextDiv = pageList.querySelector('.next');
//     const lastDiv = pageList.querySelector('div:last-of-type');
//     const queryParam = getQueryParam();
//     const pathname = location.pathname;

//     // 页码信息
//     pageInfo.innerHTML = '第 ' + nowPage + ' 页，共 ' + pageCount + ' 页';

//     // 上一页、第一页
//     if (nowPage <= 1) {
//         prevDiv.classList.add('forbidden');
//         firstDiv.classList.add('forbidden');
//     } else {
//         queryParam['page'] = nowPage - 1;
//         prevDiv.querySelector('a').href = getFullUrl(pathname, queryParam);
//         queryParam['page'] = 1;
//         firstDiv.querySelector('a').href = getFullUrl(pathname, queryParam);
//     }

//     // 下一页、最后一页
//     if (nowPage >= pageCount) {
//         nextDiv.classList.add('forbidden');
//         lastDiv.classList.add('forbidden');
//     } else {
//         queryParam['page'] = nowPage + 1;
//         nextDiv.querySelector('a').href = getFullUrl(pathname, queryParam);
//         queryParam['page'] = pageCount;
//         lastDiv.querySelector('a').href = getFullUrl(pathname, queryParam);
//     }

//     // 当前页的左边页
//     let minPage;
//     if (nowPage > 2) {
//         minPage = nowPage - 2;
//     } else {
//         minPage = 1;
//     }
//     for (let i = minPage; i < nowPage; i++) {
//         let div = document.createElement('div');
//         let a = document.createElement('a');
//         queryParam['page'] = i;
//         a.href = getFullUrl(pathname, queryParam);
//         a.innerHTML = i;
//         div.append(a);
//         pageList.insertBefore(div, nowDiv);
//     }

//     // 当前页的右边页
//     let maxPage;
//     if (nowPage <= pageCount - 2) {
//         maxPage = nowPage + 2;
//     } else {
//         maxPage = pageCount;
//     }
//     for (let i = nowPage + 1; i <= maxPage; i++) {
//         let div = document.createElement('div');
//         let a = document.createElement('a');
//         queryParam['page'] = i;
//         a.href = getFullUrl(pathname, queryParam);
//         a.innerHTML = i;
//         div.append(a);
//         pageList.insertBefore(div, nextDiv);
//     }
// }
