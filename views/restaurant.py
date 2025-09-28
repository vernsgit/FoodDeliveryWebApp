from flask import Blueprint
from flask import Flask, render_template, request, redirect, url_for, session
from service.restaurant_info import Restaurant_info
from service.menu_service import MenuService
from flask import flash
from auth import login_required



restaurant_bp= Blueprint('restaurant', __name__)

@restaurant_bp.route('/restaurants')
@login_required
def restaurants_list():
    restaurants = Restaurant_info.get_all_restaurace()
    return render_template('restaurant/restaurant_list.jinja', restaurace=restaurants)


@restaurant_bp.route('/restaurants/<int:restaurant_id>/menu', methods=['GET', 'POST'])
@login_required
def restaurant_menu(restaurant_id):
    restaurace = Restaurant_info.get_restaurace_by_id(restaurant_id)
    menu_items = MenuService.get_menu_items_client(restaurant_id)

    chod_items = [item for item in menu_items if item['typ_jidla'] == 'chod']
    piti_items = [item for item in menu_items if item['typ_jidla'] == 'pití']

    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity = request.form.get('quantity', type=int)

        if 'cart' not in session:
            session['cart'] = {}
            session['cart_restaurant_id'] = restaurant_id

        cart = session['cart']
        cart_restaurant_id = session.get('cart_restaurant_id')


        if cart and cart_restaurant_id != restaurant_id:
            flash("🚫Do košíku lze přidat položky pouze z jedné restaurace.", "danger")
            return redirect(request.url)

        # Přidání nebo aktualizace položky v košíku
        if item_id in cart:
            cart[item_id]['quantity'] += quantity
        else:
            cart[item_id] = {'quantity': quantity}

        session['cart'] = cart
        session['cart_restaurant_id'] = restaurant_id  # Ujistíme se, že ID restaurace je nastaveno
        flash("✅ Položka byla přidána do košíku.", "success")
        return redirect(request.url)

    return render_template('restaurant/menu.jinja',
                           chod_items=chod_items,
                           piti_items=piti_items,
                           restaurant=restaurace,
                           items=menu_items)

