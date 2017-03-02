from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import login_user,logout_user,login_required,current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_mail
from .forms import LoginForm,RegistrationForm,ChangePwdForm,ResetPwdForm

#登录
@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('错误的用户名或密码。')
    return render_template('auth/login.html',form=form)

#登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功。')
    return redirect(url_for('main.index'))

#注册
@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(Email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.Email,'请确认你的Flasky账户',
                  'auth/email/confirm',user=user,token=token)
        flash('验证邮件已发送至你的邮箱，请验证！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

#验证账户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您的账号已经验证成功。')
    else:
        flash('确认链接无效或已过期。')
    return redirect(url_for('main.index'))

#未验证账户跳转界面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html',user=current_user)

#重发邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.Email,'请确认你的Flasky账户',
                'auth/email/confirm',user=current_user,token=token)
    flash('验证邮件已经重新发送，请检查你的邮箱。')
    return redirect(url_for('main.index'))

#未验证用户访问不允许访问的页面时跳转至验证页面
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

#修改密码
@auth.route('/changePwd',methods=['GET','POST'])
@login_required
def changePwd():
    form = ChangePwdForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldPwd.data):
            current_user.password = form.newPwd.data
            db.session.add(current_user)
            flash('修改密码成功。')
            return redirect(url_for('main.index'))
        else:
            flash('原密码错误！')
            return redirect(url_for('auth.changePwd'))
    return render_template('auth/changePwd.html',form=form)

#重设密码
@auth.route('/resetPwd')
@login_required
def send_reset_password_emial():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.Email,
                '重设密码',
                'auth/email/resetPwd',
                user=current_user,token=token)
    flash('验证邮件已发送，请点击验证链接进行密码重设。')
    return redirect(url_for('main.index'))

@auth.route('/resetPwd/<token>',methods=['GET','POST'])
@login_required
def resetPwd(token):
    if current_user.confirm(token):
        form = ResetPwdForm()
        if form.validate_on_submit():
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('重设密码成功。')
            return redirect(url_for('main.index'))
        return render_template('auth/resetPwd.html',form=form)
    flash('确认链接无效或已过期。')
    return redirect(url_for('main.index'))
