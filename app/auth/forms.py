from flask.ext.wtf import Form
from wtforms import StringField,IntegerField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('邮箱地址',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('密码',validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    email = StringField('邮箱地址',validators=[Required(),Length(1,64),Email()])
    username = StringField('用户名',validators=[Required(),Length(1,64),
    Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$',0,'用户名只能由数字，字母，点，下划线组成，且应该以字母开头。')])
    password = PasswordField('密码',validators=[Required(),
                            EqualTo('password2',message='密码与重复密码必须一致')])
    password2 = PasswordField('重复密码',validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self,field):
        if User.query.filter_by(Email=field.data).first():
            raise ValidationError('此邮箱已被注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')


class ChangePwdForm(Form):
    oldPwd = PasswordField('原始密码',validators=[Required()])
    newPwd = PasswordField('新密码',validators=[Required(),
                        EqualTo('newPwd2',message='密码与重复密码必须一致')])
    newPwd2 = PasswordField('重复密码',validators=[Required()])
    submit = SubmitField('修改密码')


class ResetPwdForm(Form):
    password = PasswordField('新密码',validators=[Required(),
                            EqualTo('password2',message='新密码与重复密码必须一致。')])
    password2 = PasswordField('重复密码',validators=[Required()])
    submit = SubmitField('重设密码')