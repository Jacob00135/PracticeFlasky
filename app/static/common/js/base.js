(function () {
    'use strict';

    // 导航栏中，把处在当前页面的对应的标签设为选中状态(active)
    const PATH_MAP = {
        '/': 'index',
        '/auth/login': 'login',
        '/auth/register': 'register',
        '/manage_comment': 'manage-comment'
    };
    const a = document.querySelector('#nav-bar a.' + PATH_MAP[location.pathname]);
    if (a !== null) {
        a.classList.add('active');
    }
})();