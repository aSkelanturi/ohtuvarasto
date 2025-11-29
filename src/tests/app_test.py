"""Tests for the Flask web application."""
import pytest
from app import app, warehouses


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Clear warehouses before each test
        warehouses.clear()
        yield client
        # Clean up after tests
        warehouses.clear()


class TestIndexPage:
    """Tests for the index page."""

    def test_index_page_loads(self, client):
        """Test that the index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Iron Warehouse' in response.data

    def test_index_shows_empty_state_when_no_warehouses(self, client):
        """Test that the index shows empty state when there are no warehouses."""
        response = client.get('/')
        assert b'No warehouses yet' in response.data

    def test_index_shows_warehouses(self, client):
        """Test that the index shows created warehouses."""
        # Create a warehouse
        client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.get('/')
        assert b'Test Warehouse' in response.data


class TestCreateWarehouse:
    """Tests for creating warehouses."""

    def test_create_warehouse_page_loads(self, client):
        """Test that the create warehouse page loads."""
        response = client.get('/warehouse/create')
        assert response.status_code == 200
        assert b'Summon New Warehouse' in response.data

    def test_create_warehouse_successfully(self, client):
        """Test creating a warehouse successfully."""
        response = client.post('/warehouse/create', data={
            'name': 'New Warehouse',
            'capacity': '100',
            'initial_balance': '25'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'created successfully' in response.data
        assert 'New Warehouse' in warehouses

    def test_create_warehouse_without_name_fails(self, client):
        """Test that creating a warehouse without a name fails."""
        response = client.post('/warehouse/create', data={
            'name': '',
            'capacity': '100',
            'initial_balance': '0'
        })
        assert b'Warehouse name is required' in response.data

    def test_create_warehouse_with_duplicate_name_fails(self, client):
        """Test that creating a warehouse with duplicate name fails."""
        # Create first warehouse
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '0'
        })
        # Try to create another with same name
        response = client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '200',
            'initial_balance': '0'
        })
        assert b'already exists' in response.data

    def test_create_warehouse_with_invalid_capacity(self, client):
        """Test creating a warehouse with invalid capacity."""
        response = client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': 'invalid',
            'initial_balance': '0'
        })
        assert b'Invalid capacity' in response.data


class TestViewWarehouse:
    """Tests for viewing warehouses."""

    def test_view_warehouse(self, client):
        """Test viewing a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.get('/warehouse/Test')
        assert response.status_code == 200
        assert b'Test' in response.data
        assert b'50.00' in response.data

    def test_view_nonexistent_warehouse_redirects(self, client):
        """Test that viewing a nonexistent warehouse redirects."""
        response = client.get('/warehouse/NonExistent', follow_redirects=True)
        assert b'Warehouse not found' in response.data


class TestEditWarehouse:
    """Tests for editing warehouses."""

    def test_edit_warehouse_page_loads(self, client):
        """Test that the edit warehouse page loads."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.get('/warehouse/Test/edit')
        assert response.status_code == 200
        assert b'Edit Warehouse' in response.data

    def test_edit_warehouse_capacity(self, client):
        """Test editing a warehouse capacity."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.post('/warehouse/Test/edit', data={
            'name': 'Test',
            'capacity': '200'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert warehouses['Test'].tilavuus == 200

    def test_edit_warehouse_name(self, client):
        """Test renaming a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'OldName',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.post('/warehouse/OldName/edit', data={
            'name': 'NewName',
            'capacity': '100'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'NewName' in warehouses
        assert 'OldName' not in warehouses

    def test_edit_nonexistent_warehouse_redirects(self, client):
        """Test that editing a nonexistent warehouse redirects."""
        response = client.get('/warehouse/NonExistent/edit', follow_redirects=True)
        assert b'Warehouse not found' in response.data


class TestAddContent:
    """Tests for adding content to warehouses."""

    def test_add_content_successfully(self, client):
        """Test adding content to a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '0'
        })
        response = client.post('/warehouse/Test/add', data={
            'amount': '50'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Added 50' in response.data
        assert warehouses['Test'].saldo == 50

    def test_add_invalid_amount(self, client):
        """Test adding invalid amount to a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '0'
        })
        response = client.post('/warehouse/Test/add', data={
            'amount': 'invalid'
        }, follow_redirects=True)
        assert b'Invalid amount' in response.data

    def test_add_negative_amount(self, client):
        """Test adding negative amount to a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '0'
        })
        response = client.post('/warehouse/Test/add', data={
            'amount': '-10'
        }, follow_redirects=True)
        assert b'Amount must be greater than 0' in response.data


class TestRemoveContent:
    """Tests for removing content from warehouses."""

    def test_remove_content_successfully(self, client):
        """Test removing content from a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.post('/warehouse/Test/remove', data={
            'amount': '25'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Removed 25' in response.data
        assert warehouses['Test'].saldo == 25

    def test_remove_invalid_amount(self, client):
        """Test removing invalid amount from a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.post('/warehouse/Test/remove', data={
            'amount': 'invalid'
        }, follow_redirects=True)
        assert b'Invalid amount' in response.data

    def test_remove_negative_amount(self, client):
        """Test removing negative amount from a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.post('/warehouse/Test/remove', data={
            'amount': '-10'
        }, follow_redirects=True)
        assert b'Amount must be greater than 0' in response.data


class TestDeleteWarehouse:
    """Tests for deleting warehouses."""

    def test_delete_warehouse_successfully(self, client):
        """Test deleting a warehouse."""
        client.post('/warehouse/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = client.post('/warehouse/Test/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'deleted successfully' in response.data
        assert 'Test' not in warehouses

    def test_delete_nonexistent_warehouse(self, client):
        """Test deleting a nonexistent warehouse."""
        response = client.post('/warehouse/NonExistent/delete', follow_redirects=True)
        assert b'Warehouse not found' in response.data
