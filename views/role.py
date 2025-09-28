from flask import Blueprint
from flask import Flask, render_template, request, redirect, url_for, session
from service.role_service import RoleService
from service.restaurant_info import Restaurant_info
from flask import flash
from auth import login_required, roles_required
import forms



role_bp= Blueprint('role', __name__)

@role_bp.route('/profile/<int:user_id>/role-requests', methods=['GET', 'POST'])
@login_required
@roles_required(['administrátor'])
def admin_requests(user_id):
    form = forms.RequestApprovalForm(request.form)
    if request.method == 'GET':
        pending_requests = RoleService.get_pending_requests()
        return render_template('role/role_requests.jinja', zadosti=pending_requests, user_id=user_id, form=form)

    elif request.method == 'POST':
        request_id = int(form.id_zadosti.data)
        action = form.action.data

        request_details = RoleService.get_request_details(request_id)
        if not request_details:
            flash('🚫Žádost nebyla nalezena.', 'danger')
            return redirect(url_for('admin_requests', user_id=user_id))

        user__id = request_details['id_uzivatele']
        role_type = request_details['typ_role']

        if action == 'schváleno':
            previous_role = RoleService.get_current_role(user__id)

            if previous_role == 'restauratér' and role_type in ['poslíček']:
                Restaurant_info.delete_restaurace(user__id)

            if RoleService.update_request_status(request_id, 'schváleno') and RoleService.update_role(user__id, role_type):
                flash('✅Žádost byla schválena a role uživatele byla změněna.', 'success')
            else:
                flash('🚫Došlo k chybě při schvalování žádosti.', 'danger')

        # Zamítnutí žádosti
        elif action == 'zamítnuto':
            if RoleService.update_request_status(request_id, 'zamítnuto'):
                flash('✅Žádost byla zamítnuta.', 'success')
            else:
                flash('🚫Došlo k chybě při zamítání žádosti.', 'danger')

        return redirect(url_for('admin_requests', user_id=user_id))





@role_bp.route('/profile/<int:user_id>/role', methods=['GET', 'POST'])
@login_required
@roles_required(['klient', 'poslíček', 'restauratér'])
def request_role(user_id):
    all_roles = ['klient', 'poslíček', 'restauratér']
    current_role = session.get('user_role')
    available_roles = [role for role in all_roles if role != current_role]
    form = forms.RoleRequestForm(request.form)
    form.role.choices = [(role, role.capitalize()) for role in available_roles]
    # format (value, label)

    role_requests = RoleService.get_requests(user_id)
    waiting_request = any(requestt[1] == 'čekající' for requestt in role_requests)

    if request.method == 'POST' and form.validate():
        if waiting_request:
            flash("ℹ️Máte již žádost ve stavu čekající. Vyčkejte na vyhodnocení žádosti.", "info")
            return redirect(url_for('role.request_role', user_id=user_id))

        requested_role = form.role.data

        if requested_role == 'klient':
            success = RoleService.update_role(user_id, requested_role)
            if success:
                if current_role == 'restauratér':
                    Restaurant_info.delete_restaurace(user_id)

                RoleService.insert_role_request(user_id, requested_role, 'schváleno')
                session['user_role'] = 'klient'
                flash("✅Získali jste roli klient.", "success")
            else:
                flash("🚫Nastala chyba při odesílání žádosti.", "danger")
        else:
            state = 'čekající'
            success = RoleService.insert_role_request(user_id, requested_role, state)
            if success:
                flash(f"ℹ️Žádost o roli {requested_role} byla odeslána. Čeká na schválení.", "info")
            else:
                flash("🚫Nastala chyba při odesílání žádosti.", "danger")

        return redirect(url_for('profile.user_info', user_id=user_id))

    return render_template(
        'role/role.jinja',
        form=form,
        user_id=user_id,
        role_requests=role_requests
    )

