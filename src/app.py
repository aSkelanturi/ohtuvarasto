"""Flask web application for warehouse management."""
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto

app = Flask(__name__)
app.secret_key = 'warehouse-secret-key'

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
        try:
            capacity = float(request.form.get('capacity', 0))
            initial_balance = float(request.form.get('initial_balance', 0))
        except ValueError:
            flash('Invalid capacity or initial balance value.', 'error')
            return render_template('create_warehouse.html')

        if not name:
            flash('Warehouse name is required.', 'error')
            return render_template('create_warehouse.html')

        if name in warehouses:
            flash('A warehouse with this name already exists.', 'error')
            return render_template('create_warehouse.html')

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
        try:
            new_capacity = float(request.form.get('capacity', 0))
        except ValueError:
            flash('Invalid capacity value.', 'error')
            return render_template('edit_warehouse.html', name=name, warehouse=warehouse)

        if not new_name:
            flash('Warehouse name is required.', 'error')
            return render_template('edit_warehouse.html', name=name, warehouse=warehouse)

        if new_name != name and new_name in warehouses:
            flash('A warehouse with this name already exists.', 'error')
            return render_template('edit_warehouse.html', name=name, warehouse=warehouse)

        if new_capacity <= 0:
            flash('Capacity must be greater than 0.', 'error')
            return render_template('edit_warehouse.html', name=name, warehouse=warehouse)

        # Update capacity (keeping the same balance if possible)
        current_balance = warehouse.saldo
        warehouse.tilavuus = new_capacity
        if current_balance > new_capacity:
            warehouse.saldo = new_capacity
        else:
            warehouse.saldo = current_balance

        # Handle name change
        if new_name != name:
            warehouses[new_name] = warehouse
            del warehouses[name]
            flash(f'Warehouse renamed to "{new_name}" successfully.', 'success')
        else:
            flash('Warehouse updated successfully.', 'success')

        return redirect(url_for('view_warehouse', name=new_name))

    return render_template('edit_warehouse.html', name=name, warehouse=warehouse)


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
    app.run(debug=True)
