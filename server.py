from flask import Flask, render_template, Blueprint, request, abort, jsonify, flash, redirect, url_for, session, g, abort
# import ccy
import json
from markupsafe import Markup
# import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import join
# from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, PasswordField, BooleanField, TextAreaField, widgets
from decimal import Decimal
from wtforms.widgets import html_params, Select
from wtforms.validators import InputRequired, NumberRange, ValidationError, EqualTo,Email
import os
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
# from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
# from flask_dance.contrib.google import make_google_blueprint, google
# from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
# from flask.views import MethodView
from functools import wraps
# from flask_admin import BaseView, expose, Admin, AdminIndexView 
# from flask_admin.contrib.sqla import ModelView
# from flask_admin.form import rules
# from flask_babel import Babel, get_locale, lazy_gettext as _


app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = os.getenv("secret_key")
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') +'/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# app.config['WTF_CSRF_SECRET_KEY'] = 'random key for form'
cart_Blueprint = Blueprint('cart', __name__)
db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# Hello = Blueprint('Hello', __name__)
Welcome = Blueprint('Welcome', __name__)
product_blueprint = Blueprint('product', __name__)
catalog = Blueprint('catalog', __name__)



# @app.route('/')
# @app.route('/home')
# def home():
#     # kiyao = 'kiyao'
#     return render_template('homepage.html')

# Sample products
prod = [
    {'id': 1, 'name': 'Pearl Hair Clip', 'price': 12.99, 'image': 'static/img/hair clip.avif'},
    {'id': 2, 'name': 'Silk Scrunchie', 'price': 8.99, 'image': '/static/img/Silk Scrunchie.avif'},
    {'id': 3, 'name': 'Boho Headband', 'price': 9.99, 'image': '/static/img/Boho Headband.avif'},
    {'id': 4, 'name': 'French Barrette Hair Clip Gold', 'price': 13.66, 'image': '/static/img/2.5 Inch French Barrette Hair Clips Gold Color (3Pcs).jpg'},
    {'id': 5, 'name': 'Fancy Headbands', 'price': 20.99, 'image': '/static/img/Fancy Headbands.webp'},
    {'id': 6, 'name': 'Navy Blue Hair Clip', 'price': 30.99, 'image': '/static/img/Navy Blue Hair Clip.webp'},
    {'id': 7, 'name': 'Twinkling Heart Snap Hair Clips', 'price': 16.99, 'image': '/static/img/Twinkling Heart Snap Hair Clips.jpg'},
    {'id': 8, 'name': 'Emerald Large Crystal Hair Clip', 'price': 14.99, 'image': '/static/img/Emerald Large Crystal Hair Clip.webp'},
    {'id': 9, 'name': 'Handmade French Barrette Antique', 'price': 15.99, 'image': '/static/img/Handmade French Barrette Antique.avif'},
    {'id': 10, 'name': 'Romantic Red Heart Crystal Hair Claw', 'price': 23.99, 'image': '/static/img/Romantic Red Heart Crystal Hair Claw.webp'},
    {'id': 11, 'name': 'Vintage Crown Hair Clip with Crystal', 'price': 23.99, 'image': '/static/img/Vintage Crown Hair Clip with Crystal.webp'},
    {'id': 12, 'name': 'French Minimalist Long Spring Hair Clip', 'price': 23.99, 'image': '/static/img/French Minimalist Long Spring Hair Clip.webp'}

]

@app.route('/')
def homepage():
    return render_template('homepage.html', products=prod)

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(url_for('homepage'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        for product in products:
            if product['id'] == int(product_id):
                subtotal = product['price'] * quantity
                cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
                total += subtotal
                lenght = len(cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total, lenght=lenght)

@app.route('/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('view_cart'))



class CustomCategoryInput(Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for val, label, selected, render_kw in field.iter_choices():
            # Correctly generating radio button input
            html.append(
                '<label><input type="radio" {params}> {label}</label>'.format(
                    params=html_params(
                        name=field.name, value=val, checked=selected, **kwargs
                    ),
                    label=label
                )
            )
        return Markup(' '.join(html))



class CategoryField(SelectField):
    widget = CustomCategoryInput()
    def iter_choices(self):
        categories = [(c.id, c.name) for c in
        category.query.all()]
        for value, label in categories:
            yield (value, label, self.coerce(value) == self.data, {})
    
    def pre_validate(self, form):
        if self.data not in [c.id for c in category.query.all()]:
            raise ValueError(self.gettext('Not a valid choice'))

class NameForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])


class ProductForm(NameForm):
    name = StringField('Name', validators=[InputRequired()])
    price = DecimalField('Price', validators=[
    InputRequired(), NumberRange(min=Decimal('0.0'))
    ])
    category = CategoryField(
    'Category', validators=[InputRequired()], coerce=int
)
    company = StringField('Company', validators=[InputRequired()])
    image = FileField('Product Image', validators=[FileRequired()])


class CategoryForm(NameForm):
    # name = StringField('Name', validators=[InputRequired(), check_duplicate_category()])
    pass






def template_or_json(template_name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            result = f(*args, **kwargs)
            if request.accept_mimetypes.accept_json or request.is_json:
                return jsonify(result)
            return render_template(template_name, **result)
        return wrapped
    return decorator


@catalog.route('/')
@catalog.route('/<lang>/')
@catalog.route('/<lang>/home')
@template_or_json('home.html')
def home():
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products = product.query.all()
        app.logger.info('Home page with total of %d products' % len(products))
        return ({'count': len(products)})
        return render_template("home.html")

@catalog.route('/product/<id>')
def product(id):
    product = product.query.get_or_404(id)
    if not product: 
        app.logger.warning('Requested product not found.') 
        abort(404)
    return render_template('product.html', product=product)


@catalog.route('/products')
@catalog.route('/products/<int:page>')
def products(page=1):
    products = product.query.paginate(page=page, per_page=10)
    return render_template('products.html', products=products)


@catalog.route('/product-create', methods=['POST', 'GET'])
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        category = category.query.get_or_404(form.category.data)
        # company = form.company.data
        image = form.image.data
        # if allowed_file(image.filename):
        #     filename = secure_filename(image.filename)
        #     image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     product = product(name=name, price=price, category=category, image_path=filename)

        try:
            db.session.add(product)
            db.session.commit()
            # flash(_('The product %(name)s has been created', name=name), 'success')
            return redirect(url_for('catalog.product', id=product.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating product: {str(e)}', 'danger')
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('product-create.html', form=form)


@catalog.route('/<lang>/product-search')
@catalog.route('/<lang>/product-search/<int:page>')
def product_search(page=1):
    name = request.args.get('name')
    price = request.args.get('price')
    # company = request.args.get('company')
    category = request.args.get('category')
    products = product.query
    if name:
        products = products.filter(product.name.like('%' + name +
        '%'))
    if price:
        products = products.filter(product.price == price)
    # if company:
        # products = products.filter(Product.company.like('%' +
    # company + '%'))
    if category:
        products = products.select_from(join(product,
        category)).filter(
        category.name.like('%' + category + '%')
        )
    return render_template(
        'products.html', products=products.paginate(page=page, per_page= 10)
)



@catalog.route('/category-create', methods=['GET', 'POST'])
def create_category():
    form = CategoryForm(csrf_enabled=False)
    if form.validate_on_submit():
        name = form.name.data
        category = category(name)
        db.session.add(category)
        db.session.commit()
        flash('The category %s has been created' % name,
        'success')
        return redirect(url_for('catalog.category',
        id=category.id))
    if form.errors:
        flash(form.errors)
    return render_template('category-create.html', form=form)

@catalog.route('/categories')
def categories():
    categories = category.query.all()
    return render_template('categories.html', categories=categories)


@catalog.route('/category/<id>')
def category(id):
    category = category.query.get_or_404(id)
    return render_template('category.html', category=category)



app.register_blueprint(Welcome)
app.register_blueprint(cart_Blueprint)
# app.register_blueprint(product_blueprint)
# app.register_blueprint(catalog)
# app.register_blueprint(auth)
# app.register_blueprint(facebook_blueprint)
# app.register_blueprint(google_blueprint)

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()  
        # db.create_all()
        app.run(debug=True)