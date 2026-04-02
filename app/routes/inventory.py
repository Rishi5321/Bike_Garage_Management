from flask import jsonify
from app.ai.inventory_ai import process_inventory_command, execute_inventory_command, get_inventory_context

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import SparePart

inventory = Blueprint('inventory', __name__)


@inventory.route('/inventory')
def list_parts():
    parts     = SparePart.query.order_by(SparePart.name).all()
    low_stock = SparePart.query.filter(SparePart.stock <= SparePart.min_stock).all()
    return render_template('inventory/list.html', parts=parts, low_stock=low_stock)


@inventory.route('/inventory/add', methods=['GET', 'POST'])
def add_part():
    if request.method == 'POST':
        name      = request.form.get('name')
        category  = request.form.get('category')
        price     = float(request.form.get('price') or 0)
        stock     = int(request.form.get('stock') or 0)
        min_stock = int(request.form.get('min_stock') or 5)

        part = SparePart(
            name      = name,
            category  = category,
            price     = price,
            stock     = stock,
            min_stock = min_stock
        )
        db.session.add(part)
        db.session.commit()
        flash('Spare part added!', 'success')
        return redirect(url_for('inventory.list_parts'))

    return render_template('inventory/add.html')


@inventory.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
def edit_part(id):
    part = SparePart.query.get_or_404(id)
    if request.method == 'POST':
        part.name      = request.form.get('name')
        part.category  = request.form.get('category')
        part.price     = float(request.form.get('price') or 0)
        part.stock     = int(request.form.get('stock') or 0)
        part.min_stock = int(request.form.get('min_stock') or 5)
        db.session.commit()
        flash('Part updated!', 'success')
        return redirect(url_for('inventory.list_parts'))
    return render_template('inventory/edit.html', part=part)


@inventory.route('/inventory/delete/<int:id>', methods=['POST'])
def delete_part(id):
    part = SparePart.query.get_or_404(id)
    db.session.delete(part)
    db.session.commit()
    flash('Part deleted!', 'warning')
    return redirect(url_for('inventory.list_parts'))


@inventory.route('/inventory/restock/<int:id>', methods=['POST'])
def restock_part(id):
    part     = SparePart.query.get_or_404(id)
    quantity = int(request.form.get('quantity') or 0)
    part.stock += quantity
    db.session.commit()
    flash(f'{quantity} units added to {part.name}!', 'success')
    return redirect(url_for('inventory.list_parts'))

@inventory.route('/ai-inventory')

def ai_inventory():
    from app.models import SparePart
    parts = SparePart.query.all()
    return render_template('inventory/ai_inventory.html', parts=parts)


@inventory.route('/ai-inventory/command', methods=['POST'])

def ai_inventory_command():
    command = request.form.get('command')
    if not command:
        return jsonify({'success': False, 'message': 'Please enter a command!'})

    result   = process_inventory_command(command)
    response = execute_inventory_command(result, command)
    return jsonify(response)

@inventory.route('/ai-inventory/refresh')

def ai_inventory_refresh():
    from app.models import SparePart
    parts = SparePart.query.all()
    return jsonify({
        'parts': [{
            'name'      : p.name,
            'stock'     : p.stock,
            'price'     : p.price,
            'min_stock' : p.min_stock
        } for p in parts]
    })

@inventory.route('/ai-inventory/history')
# @login_required
def ai_inventory_history():
    from app.models import InventoryLog
    logs = InventoryLog.query.order_by(
        InventoryLog.created_at.desc()
    ).all()
    return render_template('inventory/ai_inventory_history.html', logs=logs)