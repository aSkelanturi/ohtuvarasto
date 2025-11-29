"""Flask web application for warehouse management."""
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Store warehouses in memory with names as keys
warehouses = {}


@app.route('/')
def index():
    """Display all warehouses."""
    return render_template('index.html', warehouses=warehouses)


@app.route('/warehouse/create', methods=['GET', 'POST'])
def create_warehouse():
    """Create a new warehouse."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        capacity_str = request.form.get('capacity', '')
        initial_balance_str = request.form.get('initial_balance', '0')
        
        form_data = {
            'name': name,
            'capacity': capacity_str,
            'initial_balance': initial_balance_str
        }
        
        try:
            capacity = float(capacity_str) if capacity_str else 0
            initial_balance = float(initial_balance_str) if initial_balance_str else 0
        except ValueError:
            flash('Invalid capacity or initial balance value.', 'error')
            return render_template('create_warehouse.html', form_data=form_data)

        if not name:
            flash('Warehouse name is required.', 'error')
            return render_template('create_warehouse.html', form_data=form_data)

        if name in warehouses:
            flash('A warehouse with this name already exists.', 'error')
            return render_template('create_warehouse.html', form_data=form_data)

        warehouses[name] = Varasto(capacity, initial_balance)
        flash(f'Warehouse "{name}" created successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('create_warehouse.html')


@app.route('/warehouse/<name>')
def view_warehouse(name):
    """View a specific warehouse."""
    if name not in warehouses:
        flash('Warehouse not found.', 'error')
        return redirect(url_for('index'))

    warehouse = warehouses[name]
    return render_template('view_warehouse.html', name=name, warehouse=warehouse)


@app.route('/warehouse/<name>/edit', methods=['GET', 'POST'])
def edit_warehouse(name):
    """Edit a warehouse's capacity."""
    if name not in warehouses:
        flash('Warehouse not found.', 'error')
        return redirect(url_for('index'))

    warehouse = warehouses[name]

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        capacity_str = request.form.get('capacity', '')
        
        edit_form = {
            'name': new_name,
            'capacity': capacity_str
        }
        
        try:
            new_capacity = float(capacity_str) if capacity_str else 0
        except ValueError:
            flash('Invalid capacity value.', 'error')
            return render_template('view_warehouse.html', name=name, warehouse=warehouse, edit_form=edit_form)

        if not new_name:
            flash('Warehouse name is required.', 'error')
            return render_template('view_warehouse.html', name=name, warehouse=warehouse, edit_form=edit_form)

        if new_name != name and new_name in warehouses:
            flash('A warehouse with this name already exists.', 'error')
            return render_template('view_warehouse.html', name=name, warehouse=warehouse, edit_form=edit_form)

        if new_capacity <= 0:
            flash('Capacity must be greater than 0.', 'error')
            return render_template('view_warehouse.html', name=name, warehouse=warehouse, edit_form=edit_form)

        # Create a new warehouse with updated capacity, preserving balance
        current_balance = min(warehouse.saldo, new_capacity)
        new_warehouse = Varasto(new_capacity, current_balance)

        # Handle name change
        if new_name != name:
            warehouses[new_name] = new_warehouse
            del warehouses[name]
            flash(f'Warehouse renamed to "{new_name}" successfully.', 'success')
        else:
            warehouses[name] = new_warehouse
            flash('Warehouse updated successfully.', 'success')

        return redirect(url_for('view_warehouse', name=new_name))

    return render_template('view_warehouse.html', name=name, warehouse=warehouse)


@app.route('/warehouse/<name>/add', methods=['POST'])
def add_content(name):
    """Add content to a warehouse."""
    if name not in warehouses:
        flash('Warehouse not found.', 'error')
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        flash('Invalid amount value.', 'error')
        return redirect(url_for('view_warehouse', name=name))

    if amount <= 0:
        flash('Amount must be greater than 0.', 'error')
        return redirect(url_for('view_warehouse', name=name))

    warehouse = warehouses[name]
    warehouse.lisaa_varastoon(amount)
    flash(f'Added {amount} to warehouse.', 'success')
    return redirect(url_for('view_warehouse', name=name))


@app.route('/warehouse/<name>/remove', methods=['POST'])
def remove_content(name):
    """Remove content from a warehouse."""
    if name not in warehouses:
        flash('Warehouse not found.', 'error')
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        flash('Invalid amount value.', 'error')
        return redirect(url_for('view_warehouse', name=name))

    if amount <= 0:
        flash('Amount must be greater than 0.', 'error')
        return redirect(url_for('view_warehouse', name=name))

    warehouse = warehouses[name]
    removed = warehouse.ota_varastosta(amount)
    flash(f'Removed {removed} from warehouse.', 'success')
    return redirect(url_for('view_warehouse', name=name))


@app.route('/warehouse/<name>/delete', methods=['POST'])
def delete_warehouse(name):
    """Delete a warehouse."""
    if name not in warehouses:
        flash('Warehouse not found.', 'error')
        return redirect(url_for('index'))

    del warehouses[name]
    flash(f'Warehouse "{name}" deleted successfully.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False)
