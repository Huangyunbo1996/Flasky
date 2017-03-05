from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash,current_app,request
from flask.ext.login import login_required,current_user
from . import main
from .forms import EditProfileForm,EditProfileAdminForm,PostForm
from .. import db
from ..models import User,Role,Permission,Post
from ..decorators import admin_required

@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html',posts=posts,form=form,pagination=pagination)

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
