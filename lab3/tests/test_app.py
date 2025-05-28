import pytest
import warnings
from app import app, users_db
from flask import url_for, session
from flask_login import current_user, login_user, login_manager
from werkzeug.security import generate_password_hash

@pytest.fixture

def client():
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain', 
        'APPLICATION_ROOT': '/',
        'PREFERRED_URL_SCHEME': 'http'
    })
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_counter_per_user(client):
    
    response = client.get('/counter')
    with client.session_transaction() as sess:
        assert sess.get('counter') == 1
    
   
    with client.session_transaction() as sess:
        sess.clear()
    
    response = client.get('/counter')
    with client.session_transaction() as sess:
        assert sess.get('counter') == 1

def test_successful_login_redirect(client):

    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    assert response.request.path == url_for('index')

def test_successful_login_message(client):
    
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    assert 'Вы успешно вошли в систему!'.encode('utf-8') in response.data

def test_failed_login_stays_on_page(client):
    
    response = client.post('/login', data={
        'username': 'wrong',
        'password': 'wrong'
    })
    assert response.request.path == url_for('login')

def test_failed_login_message(client):
   
    response = client.post('/login', data={
        'username': 'wrong',
        'password': 'wrong'
    })
    assert 'Неверное имя пользователя или пароль'.encode('utf-8') in response.data

def test_authenticated_access_to_secret(client):
    
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    # Then access secret page
    response = client.get('/secret')
    assert response.status_code == 200

def test_anonymous_access_to_secret_redirects(client):
    
    response = client.get('/secret', follow_redirects=True)
    assert response.request.path == url_for('login')
    assert 'Пожалуйста, войдите для доступа к этой странице'.encode('utf-8') in response.data

def test_redirect_to_secret_after_login(client):
    
    response = client.get('/secret')
    assert response.status_code == 302  
    
    login_url = response.location
    response = client.post(login_url, data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    
    assert response.request.path == url_for('secret')

def test_remember_me_functionality(client):
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember': 'on'
    })
    with client.session_transaction() as sess:
        assert '_user_id' in sess  


def test_successful_login_message(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    
    assert 'alert-success'.encode('utf-8') in response.data

    assert 'Вы успешно вошли в систему!'.encode('utf-8') in response.data


def test_navbar_links_for_anonymous(client):
    # Test navbar links for anonymous user
    response = client.get(url_for('index'))
    assert 'Вход'.encode('utf-8') in response.data
    assert 'Секретная страница'.encode('utf-8') not in response.data
    assert 'Выход'.encode('utf-8') not in response.data