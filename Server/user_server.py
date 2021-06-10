from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from Model.user import User, query_user


def add_user_server(app):
    app.secret_key = '1234567'

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'You are not authenticated!'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if query_user(user_id=user_id) is not None:
            curr_user = User()
            curr_user.id = user_id

            return curr_user

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user_name = request.form.get('user_name')
            remember_me = (request.form.get('remember_me', default="") != "")
            user = query_user(user_name=user_name)
            if user is not None and request.form['password'] == user['password']:

                curr_user = User()
                curr_user.id = user['id']

                # 通过Flask-Login的login_user方法登录用户
                login_user(curr_user, remember=remember_me)

                next_url = request.args.get('next', default="", type=str)
                if next_url == "":
                    return redirect(url_for('index'))
                else:
                    return redirect(next_url)

            flash('Wrong username or password!')
            flash('Please Try again!')

        # GET 请求
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")
