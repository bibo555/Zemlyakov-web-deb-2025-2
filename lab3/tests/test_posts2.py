# import pytest
# from app import app, validate_phone

# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client

# def test_url_params_display(client):
#     # Проверяем отображение параметров URL
#     response = client.get('/url_params?test1=value1&test2=value2')
#     assert b'test1' in response.data
#     assert b'value1' in response.data
#     assert b'test2' in response.data
#     assert b'value2' in response.data

# def test_headers_display(client):
#     # Проверяем отображение заголовков запроса
#     headers = {
#         'User-Agent': 'Test-Agent',
#         'Accept-Language': 'en-US'
#     }
#     response = client.get('/headers', headers=headers)
#     assert b'User-Agent' in response.data
#     assert b'Test-Agent' in response.data
#     assert b'Accept-Language' in response.data
#     assert b'en-US' in response.data

# def test_cookies_set_and_delete(client):
#     # Проверяем установку и удаление куки
#     # Первый запрос - куки нет, должна установиться
#     response = client.get('/cookies')
#     assert 'visits=1' in response.headers.get('Set-Cookie', '')
    
#     # Второй запрос - куки есть, должна удалиться
#     client.set_cookie('localhost', 'visits', '1')
#     response = client.get('/cookies')
#     assert 'visits=;' in response.headers.get('Set-Cookie', '')

# def test_form_params_display(client):
#     # Проверяем отображение параметров формы
#     data = {
#         'name': 'Test User',
#         'email': 'test@example.com'
#     }
#     response = client.post('/form', data=data)
#     assert b'Test User' in response.data
#     assert b'test@example.com' in response.data

# def test_phone_validation_valid_cases():
#     # Проверяем валидацию корректных номеров
#     test_cases = [
#         ('+7 (123) 456-75-90', None, '8-123-456-75-90'),
#         ('8(123)4567590', None, '8-123-456-75-90'),
#         ('123.456.75.90', None, '8-123-456-75-90'),
#         ('+71234567590', None, '8-123-456-75-90'),
#         ('81234567590', None, '8-123-456-75-90'),
#         ('1234567590', None, '8-123-456-75-90')
#     ]
    
#     for phone, expected_error, expected_formatted in test_cases:
#         error, formatted = validate_phone(phone)
#         assert error == expected_error
#         assert formatted == expected_formatted

# def test_phone_validation_invalid_length():
#     # Проверяем ошибку неверной длины
#     test_cases = [
#         ('+7 (123) 456-75', 'Недопустимый ввод. Неверное количество цифр. Ожидается 11 цифр'),
#         ('123.456.75', 'Недопустимый ввод. Неверное количество цифр. Ожидается 10 цифр'),
#         ('+7123456', 'Недопустимый ввод. Неверное количество цифр. Ожидается 11 цифр'),
#         ('812345678901', 'Недопустимый ввод. Неверное количество цифр. Ожидается 11 цифр')
#     ]
    
#     for phone, expected_error in test_cases:
#         error, _ = validate_phone(phone)
#         assert expected_error in error

# def test_phone_validation_invalid_chars():
#     # Проверяем ошибку недопустимых символов
#     test_cases = [
#         ('+7 (123) 456-75-9a', 'Недопустимый ввод. В номере телефона встречаются недопустимые символы'),
#         ('8(123)45675$', 'Недопустимый ввод. В номере телефона встречаются недопустимые символы'),
#         ('123#456.75.90', 'Недопустимый ввод. В номере телефона встречаются недопустимые символы')
#     ]
    
#     for phone, expected_error in test_cases:
#         error, _ = validate_phone(phone)
#         assert expected_error in error

# def test_phone_page_error_display(client):
#     # Проверяем отображение ошибки на странице
#     response = client.post('/phone', data={'phone': 'invalid'})
#     assert b'is-invalid' in response.data
#     assert b'invalid-feedback' in response.data
    

# def test_phone_page_success_display(client):
#     # Проверяем отображение успешного форматирования
#     response = client.post('/phone', data={'phone': '+7 (123) 456-75-90'})
#     assert b'alert-success' in response.data
#     assert b'8-123-456-75-90' in response.data

# def test_phone_page_preserves_input(client):
#     # Проверяем, что введенное значение сохраняется в форме
#     phone = '+7 (123) 456-75-90'
#     response = client.post('/phone', data={'phone': phone})
#     assert phone.encode('utf-8') in response.data

# def test_form_page_get_shows_form(client):
#     # Проверяем, что GET запрос показывает форму
#     response = client.get('/form')
#     assert b'<form method="POST"' in response.data
#     assert b'name="name"' in response.data
#     assert b'name="email"' in response.data

# def test_form_page_post_shows_data(client):
#     # Проверяем, что POST запрос показывает данные
#     data = {'name': 'Test', 'email': 'test@example.com'}
#     response = client.post('/form', data=data)
#     assert b'Test' in response.data
#     assert b'test@example.com' in response.data
#     assert b'<table' in response.data

# def test_cookies_page_shows_cookies(client):
#     # Проверяем отображение кук на странице
#     client.set_cookie('localhost', 'test_cookie', 'test_value')
#     response = client.get('/cookies')
#     assert b'test_cookie' in response.data
#     assert b'test_value' in response.data

# def test_headers_page_shows_request_headers(client):
#     # Проверяем, что заголовки запроса отображаются
#     headers = {'X-Test-Header': 'TestValue'}
#     response = client.get('/headers', headers=headers)
#     assert b'X-Test-Header' in response.data
#     assert b'TestValue' in response.data