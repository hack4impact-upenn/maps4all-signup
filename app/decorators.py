from functools import wraps

from flask import abort, redirect, url_for
from flask_login import current_user

from .models import Permission
# from .instances import instances
from .utils import check_user_verified_status


def permission_required(permission):
    """Restrict a view to users with the given permission."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def heroku_auth_required(f):
    """Ensures this app is a registered oauth client for this user."""

    @wraps(f)
    def decorated_view(*args, **kwargs):
        if current_user is None or current_user.heroku_refresh_token is None:
            return redirect(url_for('instances.heroku_authorize'))
        elif current_user.heroku_verified or check_user_verified_status():
            return f(*args, **kwargs)
        else:
            return redirect(url_for('instances.require_verification'))

    return decorated_view
