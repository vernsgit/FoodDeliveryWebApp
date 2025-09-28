from flask import Blueprint
from flask import Flask, render_template, request, redirect, url_for, session
from service.user_service import UserService
from flask import flash
from auth import login_required
import forms


user_bp= Blueprint('user', __name__)



@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    ##
    UserService.create_user("Adam", "Kosarek", "adam.kosarek@seznam.cz", "kdybudekonec",  "603371453",
                            "nejaka", "administrátor")
    UserService.create_user("Ondra", "Kosarek", "ondra.kosarek@seznam.cz", "kdybudekonec",  "603371453",
                            "nejaka","restauratér")
    form = forms.LoginForm(request.form)
    if request.method == 'POST':
        email = form.login.data
        password = form.password.data
        user = UserService.login(email, password)
        if user:
            session['user_id'] = user['id_uzivatele']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            flash('✅Úspěšné přihlášení.', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('🚫Neplatné přihlašovací údaje. Zkuste to znovu.', 'danger')

    return render_template('user/login.jinja', form=form)


@user_bp.route('/profile/<int:user_id>/password-change', methods=['GET', 'POST'])
@login_required
def password_change(user_id):
    form = forms.ChangePasswordForm(request.form)

    if request.method == 'POST' and form.validate():
        old_password = form.old_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        if new_password != confirm_password:
            flash('🚫 Nové heslo a potvrzené heslo se neshodují.', 'danger')
            return render_template('user/password_change.jinja', form=form, user_id=user_id)

        success = UserService.change_password(user_id, old_password, new_password)

        if success:
            flash('✅ Heslo bylo úspěšně změněno.', 'success')
            return redirect(url_for('profile.user_info', user_id=user_id))
        else:
            flash('🚫 Staré heslo je nesprávné.', 'danger')

    return render_template('user/password_change.jinja', form=form, user_id=user_id)


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        jmeno = form.name.data
        prijmeni = form.surname.data
        email = form.login.data
        password = form.password.data
        telefon = form.telephone.data

        if UserService.register_user(jmeno, prijmeni, email, password, telefon) == 2:
            flash('ℹ️Úspěšná registrace. Můžete se přihlásit.', 'info')
            return redirect(url_for('user.login'))
        elif UserService.register_user(jmeno, prijmeni, email, password, telefon) == 0:
            flash('🚫Uživatel s tímto emailem již existuje.', 'danger')
        else:
            flash('🚫Registrace se nezdrařila. Zkuste to znovu prosím.', 'danger')

    return render_template('user/register.jinja', form=form)


@user_bp.route('/logout')
def logout():
    session.pop('order', None)
    session.pop('cart', None)
    session.pop('cart_restaurant_id', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    flash('✅Úspěšné odhlášení.', 'success')
    return redirect(url_for('home_page'))