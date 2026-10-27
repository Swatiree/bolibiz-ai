from app import app


def test_home_route():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_transactions_route():
    client = app.test_client()
    response = client.get('/transactions')
    assert response.status_code == 200


def test_reports_route():
    client = app.test_client()
    response = client.get('/reports')
    assert response.status_code == 200
