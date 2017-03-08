from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash,current_app,request,make_response
from flask.ext.login import login_required,current_user
from . import main
from .forms import EditProfileForm,EditProfileAdminForm,PostForm
from .. import db
from ..models import User,Role,Permission,Post,Follow
from ..decorators import admin_required,permission_required

@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html',posts=posts,form=form,show_followed=show_followed,pagination=pagination)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page',1,type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('user.html',user=user,posts=posts,pagination=pagination)

#资料修改
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.location = form.location.data
        db.session.add(current_user)
        flash('资料修改成功。')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    return render_template('edit_profile.html',form=form,user=current_user)

#管理员修改资料
@main.route('/edit-profile/<id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.Email = form.Email.data
        user.role = Role.query.get(form.role.data)
        user.confirmed = form.confirmed.data
        user.name = form.name.data
        user.about_me = form.about_me.data
        user.location = form.location.data
        db.session.add(user)
        flash('用户资料修改成功。')
        return redirect(url_for('main.user',username=user.username))
    form.username.data = user.username
    form.Email.data = user.Email
    form.role.data = user.role.id
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.about_me.data = user.about_me
    form.location.data = user.location
    return render_template('edit_profile.html',form=form,user=user)

#用户管理
@main.route('/user-management')
@admin_required
def user_management():
    page = request.args.get('page',1,type=int)
    pagination = User.query.order_by(User.username).paginate(
        page,current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    users = pagination.items
    return render_template('user_management.html',users=users,pagination=pagination)

#文章
@main.route('/post/<id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

#编辑文章
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('文章编辑成功。')
        return redirect(url_for('main.post',id=post.id))
    form.body.data = post.body
    return render_template('edit.html',form=form)

#删除文章
@main.route('/delete-post/<int:id>')
@admin_required
def delete_post(id):
    post = Post.query.get(id)
    db.session.delete(post)
    flash('文章删除成功。')
    return redirect(url_for('main.index'))

#关注
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无法关注一个不存在的用户。')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('关注失败，不可重复关注。')
        return redirect(url_for('main.user',username=username))
    current_user.following(user)
    flash('关注成功。')
    return redirect(url_for('main.user',username=username))

#取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无法取消关注一个不存在的人。')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('无法对没有关注的人取消关注。')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    flash('取消关注成功。')
    return redirect(url_for('main.user',username=username))

#关注此用户的人列表
@main.route('/followers/<username>')
@permission_required(Permission.FOLLOW)
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在。')
        return redirect(url_for('main.index'))
    page = request.args.get('page')
    pagination = user.followers.order_by(Follow.timestamp).paginate(
        page,current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    follow = pagination.items
    return render_template('followers.html',user=user,follow=follow,pagination=pagination)

#此用户关注的人的列表
@main.route('/followed/<username>')
@permission_required(Permission.FOLLOW)
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在。')
        return redirect(url_for('main.index'))
    page = request.args.get('page')
    pagination = user.followed.order_by(Follow.timestamp).paginate(
        page,current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    follow = pagination.items
    return render_template('followed.html',user=user,follow=follow,pagination=pagination)