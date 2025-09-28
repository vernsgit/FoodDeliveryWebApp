from flask import Blueprint
import os
from flask import Flask, render_template, request, redirect, url_for, session
from service.user_info import UserInfo
from service.restaurant_info import Restaurant_info
from flask import flash
from auth import login_required, roles_required
from flask import current_app
from werkzeug.utils import secure_filename
import forms



profile_bp= Blueprint('profile', __name__)


@profile_bp.route('/profile/<int:user_id>/user-info')
@login_required
def user_info(user_id):
    user = UserInfo.get_user_info(user_id)
    if not user:
        return redirect(url_for('home_page'))

    return render_template('profile/user_info.jinja', user_id=user_id,
                           jmeno=user['jmeno'],
                           prijmeni=user['prijmeni'],
                           role=user['role'],
                           email=user['email'],
                           telefon=user['telefon'],
                           datum_registrace=user['datum_registrace'])





@login_required
@roles_required(['restauratér'])
@profile_bp.route('/profile/<int:user_id>/restaurace', methods=['GET', 'POST'])
def restaurant_info(user_id):
    form = forms.RestauraceForm(request.form)
    restaurants = Restaurant_info.get_restaurace(user_id)

    if request.method == 'POST':
        if 'delete' in request.form:
            Restaurant_info.delete_restaurace(user_id)
            flash("✅Údaje o restauraci byly vymazány.", "success")
            return redirect(request.url)

        if form.validate():
            file = request.files.get('foto_restaurace')
            foto_path = None

            if file:
                # Získání cesty k uživatelské složce
                user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
                os.makedirs(user_folder, exist_ok=True)  # Vytvoření složky, pokud neexistuje

                # Uložení souboru
                filename = secure_filename(file.filename)
                file_path = os.path.join(user_folder, filename)
                file.save(file_path)

                # Uložení relativní cesty pro statické soubory
                foto_path = os.path.relpath(file_path, start='static')

            formatted_name = form.nazev.data.strip().capitalize()
            Restaurant_info.create_restaurace(
                user_id,
                formatted_name,
                form.info.data,
                form.adresa.data,
                form.druh_kuchyne.data,
                foto_path
            )
            flash("✅Údaje o restauraci byly úspěšně uloženy.", "success")
            return redirect(request.url)

    return render_template('profile/restaurant_info.jinja', form=form, restaurace=restaurants)

