from flask import Blueprint
import os
from flask import Flask, render_template, request, redirect, url_for, session
from service.restaurant_info import Restaurant_info
from service.menu_service import MenuService
from flask import flash
from auth import login_required, roles_required
from flask import current_app
from werkzeug.utils import secure_filename
import forms



manage_menu_bp= Blueprint('manage_menu', __name__)


@manage_menu_bp.route('/manage-menu', methods=['GET', 'POST'])
@login_required
@roles_required(['restauratér'])
def manage_menu():
    user_id = session.get('user_id')
    # Načteme údaje o restauraci pro daného uživatele
    restaurant = Restaurant_info.get_restaurace(user_id)
    if not restaurant:
        flash("🚫Nejprve vyplňte údaje o restauraci.", "danger")
        return redirect(url_for('profile.restaurant_info', user_id=user_id))

    # Odstraníme ukončené akce
    MenuService.delete_expired_actions()
    # Získáme všechny položky z menu
    menu_items = MenuService.get_menu_items(restaurant['id_restaurace'])
    discount_actions = MenuService.get_discount_actions(restaurant['id_restaurace'])

    # Rozdělení položek do dvou sloupců: "chod" a "pití"
    chod_items = [item for item in menu_items if item['typ_jidla'] == 'chod']
    piti_items = [item for item in menu_items if item['typ_jidla'] == 'pití']


    if request.method == 'POST':
        if 'add_discount' in request.form:
            return redirect(url_for('manage_menu.add_discount'))
        if 'delete_discount' in request.form:
            action_id = request.form['delete_discount']
            MenuService.delete_action(action_id)
            flash("✅Slevová akce byla úspěšně zrušena.", "success")
            return redirect(request.url)

        if 'save_changes' in request.form:
            changes = False  # Sledování, zda došlo ke změnám
            for item_id, dostupnost in request.form.items():#k iteraci přes všechny páry klíč-hodnota
                if item_id.startswith('dostupnost_'):
                    item_id = int(item_id.split('_')[1])
                    dostupnost_value = int(dostupnost)

                    # Načteme původní dostupnost z databáze
                    original_availab = MenuService.get_availability(item_id)

                    if original_availab != dostupnost_value:  # Zkontrolujeme, zda se dostupnost změnila
                        MenuService.update_availability(item_id, dostupnost_value)
                        changes = True
            if changes:
                flash("✅ Změny byly úspěšně uloženy.", "success")
            else:
                flash("ℹ️ Žádné změny nebyly provedeny.", "info")
            return redirect(request.url)
        if 'add_item' in request.form:
            return redirect(url_for('manage_menu.add_menu_item'))

        if 'delete_item' in request.form:
            item_id = int(request.form['delete_item'])
            MenuService.delete_menu_item(item_id)  # Odstraníme položku z databáze
            flash("✅Položka byla odstraněna.", "success")
            return redirect(request.url)


    return render_template('manage_menu/manage_menu.jinja', chod_items=chod_items, piti_items=piti_items, discount_actions=discount_actions)

@manage_menu_bp.route('/add-menu-item', methods=['GET', 'POST'])
@login_required
@roles_required(['restauratér'])
def add_menu_item():
    user_id = session.get('user_id')
    # Načteme restauraci pro daného uživatele
    restaurant = Restaurant_info.get_restaurace(user_id)
    if not restaurant:
        flash("🚫Nejprve vyplňte údaje o restauraci.", "danger")
        return redirect(url_for('restaurant_info', user_id=user_id))

    form = forms.MenuItemForm(request.form)
    if request.method == 'POST':
        if form.validate():
            file = request.files.get('foto_jidla')
            foto_path = None

            # Pokud je soubor nahrán, uložíme ho na server
            if file:
                user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
                os.makedirs(user_folder, exist_ok=True)  # Pokud složka neexistuje, vytvoříme ji
                filename = secure_filename(file.filename)
                file_path = os.path.join(user_folder, filename)
                file.save(file_path)  # Uložení souboru na disk
                foto_path = os.path.relpath(file_path, start='static')  # Cesta k souboru relativně k "static"

            formatted_name = form.nazev.data.strip().capitalize() #strip odebere mezery na zacatku a konci
            success = MenuService.add_menu_item(
                restaurant_id=restaurant['id_restaurace'],
                name=formatted_name,
                price=form.cena.data,
                cost=form.cena_nakladu.data,
                item_type=form.typ_jidla.data,
                photo_path=foto_path
            )

            if success:
                flash("✅Položka byla úspěšně přidána.", "success")
                return redirect(url_for('manage_menu.manage_menu'))  # Po úspěšném přidání se přesměruje na správu menu
            else:
                flash("🚫Překročili jste limit 24 položek.", "danger")

    return render_template('manage_menu/add_menu_item.jinja', form=form)  # Zobrazí formulář pro přidání položky

@manage_menu_bp.route('/add-discount', methods=['GET', 'POST'])
@login_required
@roles_required(['restauratér'])
def add_discount():
    user_id = session.get('user_id')
    restaurant = Restaurant_info.get_restaurace(user_id)
    if not restaurant:
        flash("🚫 Nejprve vyplňte údaje o restauraci.", "danger")
        return redirect(url_for('restaurant_info', user_id=user_id))

    menu_items = MenuService.get_menu_items(restaurant['id_restaurace'])
    if not menu_items:
        flash("🚫 Pro vytváření akce, musíte přidat chod nebo pití.", "danger")
        return redirect(url_for('manage_menu'))

    form = forms.DiscountForm(request.form)
    if request.method == 'POST' and form.validate():
        # Získání ID jídel vybraných pro akci
        selected_items = request.form.getlist('jidla')
        if not selected_items:
            flash("🚫 Musíte vybrat alespoň jedno jídlo pro vytvoření akce.", "danger")
        else:
            discount_action_id = MenuService.add_discount_action(
                restaurant_id=restaurant['id_restaurace'],
                name=form.nazev.data.strip(),
                discount=form.sleva_procenta.data,
                start=form.zacatek.data,
                end=form.konec.data,
                item_ids=selected_items
            )
            if discount_action_id:
                flash("✅Akce byla úspěšně přidána.", "success")
                return redirect(url_for('manage_menu'))
            else:
                flash("🚫Vyberte jiný časový rozsah, zasahujete již do zadané akce.", "danger")


    return render_template('manage_menu/add_discount.jinja', form=form, jidla=menu_items)

