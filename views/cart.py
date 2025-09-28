from flask import Blueprint

from flask import Flask, render_template, request, redirect, url_for, session

from service.user_info import UserInfo
from service.orders import Orders
from service.restaurant_info import Restaurant_info
from flask import flash
from auth import login_required, roles_required

import forms



cart_bp= Blueprint('cart', __name__)



@cart_bp.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    cart = session.get('cart', {})

    items = []
    total_price = 0.0

    for item_id, details in cart.items():
        item_data = Orders.cart_item(item_id)
        if item_data:
            quantity = details['quantity']
            price = item_data['cena']
            sleva = item_data['akce']['sleva_procenta'] if item_data['akce'] else 0
            discounted_price = price * (1 - sleva / 100)

            items.append({
                'id_jidla': item_data['id_jidla'],
                'nazev': item_data['nazev'],
                'foto_jidla': item_data['foto_jidla'],
                'cena': price,
                'mnozstvi': quantity,
                'cena_itemu': discounted_price * quantity * 1.15,
                'akce': item_data['akce']
            })
            total_price += discounted_price * quantity * 1.15
    if request.method == 'POST':
        return redirect(url_for('cart.order'))

    return render_template('cart/cart.jinja', items=items, total_price=total_price)

@cart_bp.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    session.pop('cart', None)
    session.pop('cart_restaurant_id', None)
    session.pop('order', None)
    flash("✅Košík byl vyprázdněn.", "success")
    return redirect(url_for('cart'))

@cart_bp.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    user_id = session.get('user_id')
    user_info = UserInfo.get_user_info(user_id)
    restaurant_id = session.get('cart_restaurant_id')
    restaurace = Restaurant_info.get_restaurace_by_id(restaurant_id)


    #Načtení košíku
    cart = session.get('cart', {})
    items = []
    total_price = 0.0

    for item_id, details in cart.items():
        item_data = Orders.cart_item(item_id)
        if item_data:
            quantity = details['quantity']
            price = item_data['cena']
            sleva = item_data['akce']['sleva_procenta'] if item_data['akce'] else 0
            discounted_price = price * (1 - sleva / 100)

            items.append({
                'id_jidla': item_data['id_jidla'],
                'nazev': item_data['nazev'],
                'foto_jidla': item_data['foto_jidla'],
                'cena': price,
                'cena_nakladu': item_data['cena_nakladu'],
                'mnozstvi': quantity,
                'cena_itemu': discounted_price * quantity * 1.15,
                'akce': item_data['akce']
            })
            total_price += discounted_price * quantity * 1.15

    form = forms.OrderForm(data={'telefon': user_info[4]})
    transport_costs = 0 if total_price >= 500 else 45
    if request.method == 'POST' and form.validate():
        telefon = form.telefon.data
        adresa = form.adresa.data
        zpusob_platby = form.zpusob_platby.data
        session['order'] = True

        if zpusob_platby == 'dobirka':
            # Aktualizace uživatelských údajů
            UserInfo.update_info(user_id, telefon, adresa)

            # Uložení objednávky do databáze
            order_id = Orders.save_order(user_id, restaurant_id, items, transport_costs, total_price, zpusob_platby)

            flash(f"✅ Vaše objednávka č. {order_id} byla úspěšně odeslána!", "success")
            session.pop('order', None)
            session.pop('cart', None)
            session.pop('cart_restaurant_id', None)
            return redirect(url_for('home_page'))
        else:
            return redirect(url_for('payment'))

    return render_template(
        'cart/order.jinja',
        form=form,
        user_info=user_info,
        restaurant=restaurace,
        items=items,
        transport_costs=transport_costs,
        total_price=total_price
    )

@cart_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if not session.get('order'):
        flash("🚫Nejprve  vyplňte údaje v objednávkovém formuláři.", "danger")
        return redirect(url_for('order'))

    user_id = session.get('user_id')
    restaurant_id = session.get('cart_restaurant_id')
    cart = session.get('cart', {})

    items = []
    total_price = 0.0
    for item_id, details in cart.items():
        item_data = Orders.cart_item(item_id)
        if item_data:
            quantity = details['quantity']
            price = item_data['cena']
            sleva = item_data['akce']['sleva_procenta'] if item_data['akce'] else 0
            discounted_price = price * (1 - sleva / 100)
            items.append({
                'id_jidla': item_data['id_jidla'],
                'nazev': item_data['nazev'],
                'foto_jidla': item_data['foto_jidla'],
                'cena': price,
                'cena_nakladu': item_data['cena_nakladu'],
                'mnozstvi': quantity,
                'cena_itemu': discounted_price * quantity * 1.15,
                'akce': item_data['akce']
            })
            total_price += discounted_price * quantity * 1.15

    transport_costs = 0 if total_price >= 500 else 45
    if request.method == 'POST':
        zpusob_platby = 'online'

        order_id = Orders.save_order(
            user_id, restaurant_id, items, transport_costs, total_price, zpusob_platby
        )
        session.pop('cart', None)
        session.pop('cart_restaurant_id', None)
        flash(f"✅ Vaše objednávka č. {order_id} byla úspěšně dokončena!", "success")
        return redirect(url_for('home_page'))  # Přesměrování na hlavní stránku po úspěšném zaplacení

    return render_template(
        'cart/payment.jinja',
        total_price=total_price,
        transport_costs=transport_costs
    )


@cart_bp.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    user_id = session.get('user_id')
    orders = Orders.get_user_orders(user_id)

    return render_template('cart/orders_list.jinja', orders=orders)