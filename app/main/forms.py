from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField,ValidationError
from wtforms.validators import Required,Length,Regexp,Email
from ..models import Role,User

class EditProfileForm(Form):
    name = StringField('姓名',validators=[Length(0,64)])
    about_me = TextAreaField('关于我')
    location = StringField('居住地',validators=[Length(0,64)])
    submit = SubmitField('确定')


class EditProfileAdminForm(Form):
    username = StringField('用户名',validators=[Required(),Length(1,64),
    Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$',0,'用户名只能由数字，字母，点，下划线组成，且应该以字母开头。')])
    Email = StringField('邮箱地址',validators=[Required(),Length(1,64),Email()])
    name = StringField('姓名',validators=[Length(0,64)])
    about_me = TextAreaField('关于我')
    location = StringField('居住地',validators=[Length(0,64)])
    confirmed = BooleanField('验证')
    role = SelectField('权限',coerce=int)
    submit = SubmitField('确定')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name) 
                            for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.Email and \
         User.query.filter_by(Email=field.data).first():
            raise ValidationError('此邮箱已被注册。')

    def validate_username(self,field):
        if field.data != self.user.username and \
        User.query.filter_by(username=field.data).first():
            raise ValidationError
        
        
class PostForm(Form):
    body = PageDownField('想说点什么？',validators=[Required()])
    submit = SubmitField('提交')


class CommentForm(Form):
    body = StringField('发表评论',validators=[Required()])
    submit = SubmitField('发表评论')