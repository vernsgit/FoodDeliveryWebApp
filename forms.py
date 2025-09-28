from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, DateTimeLocalField, FloatField, SelectField, TextAreaField, FileField, HiddenField, SubmitField, validators
from wtforms.fields.simple import PasswordField, EmailField
from wtforms.validators import Email, NumberRange
from wtforms import ValidationError
from flask import request
class LoginForm(FlaskForm):
    login = EmailField(name='login', label='Email', validators=[validators.InputRequired(), Email()])
    password = PasswordField(name='password', label='Heslo',
                             validators=[validators.Length(max=50), validators.InputRequired()])

class RegisterForm(FlaskForm):
    name = StringField(name='name', label='Jméno',
                       validators=[validators.InputRequired(), validators.Length(min=2, max=50)])
    surname = StringField(name='surname', label='Příjmení',
                          validators=[validators.InputRequired(), validators.Length(min=2, max=50)])
    login = EmailField(name='login', label='Email', validators=[validators.InputRequired(), Email()])

    telephone = StringField(name='telephone', label='Telefon',
                            validators=[validators.InputRequired(), validators.Length(min=9, max=15)])

    password = PasswordField(name='password', label='Heslo',
                             validators=[validators.InputRequired(), validators.Length(min=8, max=50)])

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Staré heslo', validators=[validators.InputRequired(), validators.Length(min=8, max=50)])
    new_password = PasswordField('Nové heslo', validators=[validators.InputRequired(), validators.Length(min=8, max=50)])
    confirm_password = PasswordField('Potvrzení nového hesla', validators=[validators.InputRequired()])

class RoleRequestForm(FlaskForm):
    role = SelectField(
        name='role', label='Vyberte roli', choices=[], #Dynamicky doplněno v route
        validators=[validators.InputRequired()]
    )

class RequestApprovalForm(FlaskForm):
    id_zadosti = HiddenField(validators=[validators.InputRequired()])
    action = HiddenField(validators=[validators.InputRequired()])


def file_required(form, field):
    field_name = field.name
    if field_name not in request.files or not request.files[field_name].filename:
        raise ValidationError(f"Nahrání fotografie pro {field.label.text} je povinné.")
    file = request.files[field_name]
    if not file.filename.lower().endswith(('png', 'jpg', 'jpeg')):
        raise ValidationError("Povolené formáty jsou: png, jpg, jpeg.")
class RestauraceForm(FlaskForm):
    nazev = StringField(name='nazev', label='Název restaurace', validators=[validators.InputRequired(), validators.Length(max=100)])
    info = TextAreaField(name='info', label='Popis restaurace', validators=[validators.Optional(), validators.Length(max=500)])
    adresa = StringField(name='adresa', label='Adresa restaurace', validators=[validators.InputRequired(), validators.Length(max=200)])
    druh_kuchyne = StringField(name='druh_kuchyne', label='Druh kuchyně', validators=[validators.InputRequired(), validators.Length(max=100)])
    foto_restaurace = FileField(name='foto_restaurace', label='Fotografie restaurace',validators=[file_required])

class MenuItemForm(FlaskForm):
    nazev = StringField(name="nazev", label='Název', validators=[validators.InputRequired(), validators.Length(max=20)])
    cena = FloatField(name="cena", label='Cena', validators=[validators.InputRequired(), NumberRange(min=1)])
    cena_nakladu = FloatField(name="cena_nakladu", label='Cena nákladů', validators=[validators.InputRequired(), NumberRange(min=0)])
    typ_jidla = SelectField(name="typ_jidla", label='Typ jídla', choices=[('chod', 'Chod'), ('pití', 'Pití')])
    foto_jidla = FileField(name="foto_jidla", label='Fotografie jídla', validators=[file_required])


class DiscountForm(FlaskForm):
    nazev = StringField("Název akce", validators=[validators.InputRequired(), validators.Length(max=100)])
    sleva_procenta = IntegerField("Sleva (%)", validators=[validators.InputRequired(), NumberRange(min=1, max=100)])
    zacatek = DateTimeLocalField("Začátek akce", format='%Y-%m-%dT%H:%M', validators=[validators.InputRequired()])
    konec = DateTimeLocalField("Konec akce", format='%Y-%m-%dT%H:%M', validators=[validators.InputRequired()])

    def validate_zacatek(form, field):
        if field.data < datetime.now():
            raise ValidationError("Datum a čas začátku nemůže být v minulosti.")

    def validate_konec(form, field):
        if form.zacatek.data and field.data < form.zacatek.data:
            raise ValidationError("Datum a čas konce musí být pozdější než datum a čas začátku.")
        elif form.zacatek.data and field.data == form.zacatek.data:
            raise ValidationError("Datum a časy se nesmí rovnat.")

class OrderForm(FlaskForm):
    telefon = StringField(
        'Telefon',
        validators=[
            validators.InputRequired(message='Telefon je povinný.'),validators.Length(min=9, max=15, message='Telefon musí mít délku mezi 9 a 15 znaky.')
        ])
    adresa = StringField(
        'Adresa',
        validators=[
            validators.input_required(message='Adresa je povinná.'),validators.Length(min=5, max=100, message='Adresa musí mít délku mezi 5 a 100 znaky.')
        ]
    )
    zpusob_platby = SelectField(
        'Způsob platby',
        choices=[('dobirka', 'Dobirka'), ('online', 'Online')],
        validators=[validators.InputRequired(message='Způsob platby je povinný.')]
    )