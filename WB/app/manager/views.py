from flask import render_template, url_for, redirect, flash, request
from app import db
from . import manager
from app.decorators import decorator_admin, decorator_permission
from app.models import Permission
from .forms import EditUserForm
from flask import abort
from app.models import User

@manager.route('/edit_user', methods=['GET', 'POST'])
@decorator_admin
def edit_user() :
    id = request.args.get('id')
    if id is None :
        abort(404)
    user = User.query.filter_by(id=id).first()
    if user is None :
        abort(404)

    form = EditUserForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.location = form.location.data
        user.role_id = form.role_id.data
        user.about_me = form.about_me.data
        if len(form.password.data) != 0 :
            user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.user_info', id=user.id))

    form.name.data = user.name
    form.email.data = user.email
    form.location.data = user.location
    form.role_id.data = user.role_id
    form.about_me.data = user.about_me
    form.confirmed.data = user.confirmed
    return render_template('manager/edit_user.html', form=form)

@manager.route('/index')
@decorator_admin
def index() :
    return 'i am admin'

from app.models import Comment
@manager.route('/manager_comment')
@decorator_permission(Permission.MODE_COMMENT)
def manager_comment():
    page = request.args.get('page', type=int, default=1)
    #desc 倒叙遍历
    paginate = Comment.query.order_by(Comment.id.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template('manager/manager_comment.html', paginate=paginate)
from flask_login import current_user

@manager.route('/delete_comment', methods=['GET', 'POST'])
def delete_comment():
    id = request.args.get('id')
    if id is None:
        abort(404)
    comment = Comment.query.filter_by(id=id).first()
    if comment is None:
        abort(404)
    if comment.user_id==current_user.id or comment.user.role_id==3:
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('.manager_comment'))
    return redirect(url_for('.manager_comment'))