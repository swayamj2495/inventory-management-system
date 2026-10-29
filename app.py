from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from threading import Lock
import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

app = Flask(__name__)


# --- Database Configuration ---
db_user     = os.environ.get('DB_USER',     'inventory_user')
db_password = os.environ.get('DB_PASSWORD', 'inventory_pass')
db_host     = os.environ.get('DB_HOST',     '127.0.0.1')
db_port     = os.environ.get('DB_PORT',     '3307')
db_name     = os.environ.get('DB_NAME',     'inventory_db')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
order_lock = Lock()


# --- Database Models ---
class Product(db.Model):
    __tablename__ = 'Products'
    product_id    = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text)
    price         = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    __tablename__ = 'Orders'
    order_id    = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    order_date  = db.Column(db.DateTime, server_default=db.func.now())
    status      = db.Column(db.String(50), nullable=False)
    items       = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__  = 'Order_Items'
    order_item_id  = db.Column(db.Integer, primary_key=True)
    order_id       = db.Column(db.Integer, db.ForeignKey('Orders.order_id'))
    product_id     = db.Column(db.Integer, db.ForeignKey('Products.product_id'))
    quantity       = db.Column(db.Integer, nullable=False)
    price          = db.Column(db.Numeric(10, 2), nullable=False)


# ============================================================
# UI Routes (serve Jinja2 templates)
# ============================================================

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/products')
def products_page():
    """Products management page."""
    return render_template('products.html', active_page='products')

@app.route('/place-order')
def place_order_page():
    """Place order page."""
    return render_template('place_order.html', active_page='place_order')

@app.route('/reports')
def reports_page():
    """Reports page."""
    return render_template('reports.html', active_page='reports')

# Legacy template routes referenced in old templates — redirect to new ones
@app.route('/ui/report')
def ui_report():
    return redirect(url_for('reports_page'))

@app.route('/ui/add-product')
def ui_add_product():
    return redirect(url_for('products_page'))


# ============================================================
# JSON API Routes (original + new /api/* equivalents)
# ============================================================

@app.route('/add_product', methods=['POST'])
def add_product():
    """Create a new product. Accepts JSON, returns JSON."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input — JSON body required"}), 400

    name           = data.get('name', '').strip()
    description    = data.get('description', '').strip()
    raw_price      = data.get('price')
    raw_stock      = data.get('stock_quantity')

    # Server-side validation
    if not name:
        return jsonify({"error": "Product name is required"}), 400
    if raw_price is None:
        return jsonify({"error": "Price is required"}), 400
    try:
        price = float(raw_price)
        if price < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Price must be a non-negative number"}), 400
    if raw_stock is None:
        return jsonify({"error": "Stock quantity is required"}), 400
    try:
        stock_quantity = int(raw_stock)
        if stock_quantity < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Stock quantity must be a non-negative integer"}), 400

    try:
        product = Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added", "product_id": product.product_id}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Database error while saving product"}), 500


@app.route('/place_order', methods=['POST'])
def place_order():
    """Place an order. Accepts JSON, returns JSON."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input — JSON body required"}), 400

    customer_id = data.get('customer_id')
    items       = data.get('items')

    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400
    try:
        customer_id = int(customer_id)
        if customer_id < 1:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "customer_id must be a positive integer"}), 400

    if not items or not isinstance(items, list) or len(items) == 0:
        return jsonify({"error": "items must be a non-empty list"}), 400

    with order_lock:
        try:
            order = Order(customer_id=customer_id, status="Processing")
            db.session.add(order)
            db.session.flush()  # Obtain order_id before inserting items

            for item in items:
                product_id = item.get('product_id')
                quantity   = item.get('quantity')

                if not product_id or not quantity:
                    db.session.rollback()
                    return jsonify({"error": "Each item must have product_id and quantity"}), 400
                try:
                    quantity = int(quantity)
                    if quantity < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    db.session.rollback()
                    return jsonify({"error": f"Quantity for product {product_id} must be a positive integer"}), 400

                product = Product.query.filter_by(product_id=product_id).with_for_update().first()
                if not product:
                    db.session.rollback()
                    return jsonify({"error": f"Product {product_id} not found"}), 404
                if product.stock_quantity < quantity:
                    db.session.rollback()
                    return jsonify({
                        "error": f"Insufficient stock for \"{product.name}\" "
                                 f"(requested {quantity}, available {product.stock_quantity})"
                    }), 400

                product.stock_quantity -= quantity
                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=product_id,
                    quantity=quantity,
                    price=product.price
                )
                db.session.add(order_item)

            order.status = "Completed"
            db.session.commit()
            return jsonify({"message": "Order placed", "order_id": order.order_id}), 201

        except Exception:
            db.session.rollback()
            return jsonify({"error": "Database error while placing order"}), 500


@app.route('/report', methods=['GET'])
def report():
    """Original JSON report endpoint — preserved for backward compatibility."""
    try:
        products = Product.query.all()
        orders   = Order.query.all()
        product_list = [
            {
                "product_id":    p.product_id,
                "name":          p.name,
                "stock_quantity": p.stock_quantity
            }
            for p in products
        ]
        order_list = [
            {
                "order_id":   o.order_id,
                "customer_id": o.customer_id,
                "status":     o.status,
                "order_date": str(o.order_date) if o.order_date else None
            }
            for o in orders
        ]
        return jsonify({"products": product_list, "orders": order_list}), 200
    except Exception:
        return jsonify({"error": "Database error while fetching report"}), 500


@app.route('/api/report', methods=['GET'])
def api_report():
    """
    Extended JSON report used by the UI.
    Includes price on products and ISO-formatted order_date on orders.
    Low-stock threshold: products with stock_quantity <= 5 are flagged.
    """
    try:
        products = Product.query.order_by(Product.product_id).all()
        orders   = Order.query.order_by(Order.order_id).all()

        product_list = [
            {
                "product_id":     p.product_id,
                "name":           p.name,
                "description":    p.description or '',
                "price":          float(p.price) if p.price is not None else None,
                "stock_quantity": p.stock_quantity
            }
            for p in products
        ]
        order_list = [
            {
                "order_id":    o.order_id,
                "customer_id": o.customer_id,
                "status":      o.status,
                "order_date":  o.order_date.isoformat() if o.order_date else None
            }
            for o in orders
        ]
        return jsonify({"products": product_list, "orders": order_list}), 200
    except Exception:
        return jsonify({"error": "Database error while fetching data"}), 500


if __name__ == '__main__':
    # Uncomment the following lines to create/update tables on first run:
    # with app.app_context():
    #     db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
