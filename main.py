from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from sqlalchemy.sql import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://ecom_user:securepassword@localhost/ecommerce_api'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    orders = db.relationship('Order', back_populates = 'user')
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date  = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', back_populates='orders')
    products = db.relationship('Product', secondary='order_product', back_populates="orders" )
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    orders = db.relationship('Order', secondary='order_product', back_populates='products')
    
class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
with app.app_context():
    db.create_all()

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        
    orders = fields.List(fields.Nested('OrderSchema', exclude=('user',)))
        

class OrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model=Order
        include_fk = True
        load_instance = True
    
    products = fields.List(fields.Nested('ProductSchema', exclude=('orders',)))
    
    
class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        include_fk = True
        load_instance = True
        
    orders = fields.List(fields.Nested('OrderSchema', exclude=('products',)))
    
    
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return users_schema.jsonify(users)

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    new_user = user_schema.load(data, session=db.session)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    user = User.query.get(id)
    data = request.get_json()
    user = user_schema.load(data, instance=user, session=db.session)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted."})



@app.route("/orders/user/<int:user_id>", methods=["GET"])
def get_order_by_user(user_id):
    orders = Order.query.filter_by(user_id= user_id).all()
    return orders_schema.jsonify(orders)
   
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    new_order = order_schema.load(data, session=db.session)
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 201

@app.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["PUT"])
def add_product_to_order(order_id, product_id):
    order = Order.query.get(order_id)
    product = Product.query.get(product_id)
    if product not in order.products:
        order.products.append(product)
        db.session.commit()
    return order_schema.jsonify(order)

@app.route("/orders/<int:order_id>/remove_product/<int:product_id>", methods=["DELETE"])
def remove_product_from_order(order_id, product_id):
    order = Order.query.get(order_id)
    product = Product.query.get(product_id)
    if product in order.products:
        order.products.remove(product)
        db.session.commit()
    return order_schema.jsonify(order)

@app.route("/orders/<int:order_id>/products", methods=["GET"])
def get_products_in_order(order_id):
    order = Order.query.get(order_id)
    return products_schema.jsonify(order.products)



@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route("/products/<int:id>", methods=["GET"])
def get_product_by_id(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()
    new_product = product_schema.load(data, session=db.session)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product), 201

@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get(id)
    data = request.get_json()
    product = product_schema.load(data, instance=product, session=db.session)
    db.session.commit()
    return product_schema.jsonify(product)

@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted.'})





if __name__ == '__main__':
    app.run(debug=True)
    

    

    
        


