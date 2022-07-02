from datetime import datetime
from flask import render_template, request, abort, url_for
from flask_login import current_user
from . import main
from .. import db
from ..models import Permission, Article, Comment
from ..decorators import permission_required
from config import Config


@main.route('/')
def index():
    # 查询数据库中的文章列表
    filter_param = request.args.get('filter', 'all', type=str)
    if not current_user.is_authenticated:
        filter_param = 'all'
        bq = Article.query.order_by(Article.publish_time.desc())
    else:
        if filter_param == 'follow_author':
            bq = current_user.follow_author_articles
        else:
            filter_param = 'all'
            bq = Article.query.order_by(Article.publish_time.desc())
    
    # 获取符合条件的记录总个数，计算页数
    page_count = bq.count() / Config.FLASKY_MAX_ARTICLE_NUMBER
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    else:
        page_count = int(page_count)

    # 获取当前页的条目
    page = request.args.get('page', 1, type=int)
    if page < 1 or page > page_count:
        page = 1
    article_list = bq.paginate(
        page,
        per_page=Config.FLASKY_MAX_ARTICLE_NUMBER,
        error_out=False
    ).items

    return render_template('main/index.html', article_list=article_list, page_count=page_count, current_page=page, filter_param=filter_param)


@main.route('/publish_article', methods=['POST'])
def publish_article():
    # 检查权限
    if not current_user.can(Permission.WRITE):
        return {'status': 0, 'message': '没有权限'}

    # 检查数据
    title = request.json['article-title']
    length = len(title)
    if length <= 0 or length > 40:
        return {'status': 0, 'message': '文章标题长度必须在[1, 125]之间！'}
    content = request.json['article-content']
    if not content:
        return {'status': 0, 'message': '文章内容不能为空！'}

    # 添加文章
    article = Article(title=title, content=content, publish_time=datetime.utcnow(), author_id=current_user.customer_id)
    db.session.add(article)
    db.session.commit()
    return {'status': 1, 'message': '发布成功，即将刷新页面'}


@main.route('/article/<int:article_id>')
def show_article(article_id):
    # 检查参数
    article = Article.query.filter_by(article_id=article_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    bq = Comment.query.filter_by(article_id=article_id, disabled=False).order_by(Comment.comment_time.desc())
    comment_list = bq.paginate(page, per_page=Config.FLASKY_MAX_COMMENT_NUMBER, error_out=False).items
    page_count = bq.count() / Config.FLASKY_MAX_COMMENT_NUMBER
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    else:
        page_count = int(page_count)

    return render_template(
        'main/article.html',
        article=article,
        comment_list=comment_list,
        current_page=page,
        page_count=page_count
    )


@main.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
@permission_required(Permission.WRITE)
def edit_article(article_id):
    # 检查参数
    article = Article.query.filter_by(article_id=article_id).first_or_404()

    # GET
    if request.method == 'GET':
        if article.author.customer_id == current_user.customer_id or current_user.is_administrator():
            return render_template('main/edit-article.html', article=article)
        abort(403)

    # POST
    if article.author.customer_id != current_user.customer_id and not current_user.is_administrator():
        return {'status': 0, 'message': '无权操作'}
    content = request.json['article-content']
    if not content:
        return {'status': 0, 'message': '内容不能为空！'}
    article.content = content
    db.session.add(article)
    db.session.commit()
    return {'status': 1, 'message': '修改成功', 'next': url_for('main.show_article', article_id=article.article_id)}


@main.route('/publish_comment/<int:article_id>', methods=['POST'])
@permission_required(Permission.COMMENT)
def publish_comment(article_id):
    # 检查文章id
    article = Article.query.filter_by(article_id=article_id).first()
    if article is None:
        return {'status': 0, 'message': '要评论的文章不存在！'}

    # 检查评论内容
    content = request.json['comment-content']
    if not content:
        return {'status': 0, 'message': '评论内容不能为空！'}

    # 添加评论
    comment = Comment(content=content, author_id=current_user.customer_id, article_id=article_id, comment_time=datetime.utcnow())
    db.session.add(comment)
    db.session.commit()
    return {'status': 1, 'message': '评论成功，即将刷新页面'}


@main.route('/manage_comment')
@permission_required(Permission.MODERATE)
def manage_comment_page():
    page = request.args.get('page', 1, type=int)
    bq = Comment.query.order_by(Comment.comment_time.desc())
    comment_list = bq.paginate(
        page,
        per_page=Config.FLASKY_MAX_COMMENT_NUMBER,
        error_out=False
    ).items
    page_count = bq.count() / Config.FLASKY_MAX_COMMENT_NUMBER
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    else:
        page_count = int(page_count)

    return render_template(
        'main/manage-comment.html',
        comment_list=comment_list,
        current_page=page,
        page_count=page_count
    )


@main.route('/update_comment_disabled', methods=['POST'])
@permission_required(Permission.MODERATE)
def disable_comment():
    # 检查参数
    comment = Comment.query.filter_by(comment_id=request.json['comment_id']).first()
    if comment is None:
        return {'status': 0, 'message': '要禁用的评论不存在！'}

    # 禁用评论
    comment.disabled = bool(request.json['disabled'])
    db.session.add(comment)
    db.session.commit()

    return {'status': 1, 'message': '成功'}
