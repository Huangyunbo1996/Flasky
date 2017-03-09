from functools import wraps
from flask_login import current_user
from flask import abort
from .models import Permission

def permission_required(permissions):
    def decorator(f):
        @wraps(f)
        def decorated_funcation(*args,**kwargs):
            if not current_user.can(permissions):
                abort(403)
            return f(*args,**kwargs)
        return decorated_funcation
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)