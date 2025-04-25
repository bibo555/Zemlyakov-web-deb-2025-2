# import pytest
# from app import app as flask_app
# from flask import url_for

# @pytest.fixture
# def app():
#     yield flask_app

# @pytest.fixture
# def client(app):
#     return app.test_client()

# def test_index_page(client):
#     response = client.get(url_for('index'))
#     assert response.status_code == 200
#     assert "Disscusion for everyone" in response.data.decode('utf-8')

# def test_posts_page(client):
#     response = client.get(url_for('posts'))
#     assert response.status_code == 200
#     assert "Последние посты" in response.data.decode('utf-8')

# def test_nonexistent_post(client):
#     response = client.get(url_for('post', index=999))
#     assert response.status_code == 404
#     assert "404 Not Found" in response.data.decode('utf-8')

# def test_post_page_content(client):
#     response = client.get(url_for('post', index=0))
#     assert "Автор:" in response.data.decode('utf-8')
#     assert "Опубликовано:" in response.data.decode('utf-8')
#     assert "Комментарии" in response.data.decode('utf-8')

# def test_post_page_date_format(client):
#     response = client.get(url_for('post', index=0))
#     assert "Опубликовано: " in response.data.decode('utf-8')
#     # Проверка формата даты
#     assert "." in response.data.decode('utf-8')  # Проверка наличия точек в дате

# def test_post_page_image(client):
#     response = client.get(url_for('post', index=0))
#     assert '<img class="img fluid"' in response.data.decode('utf-8')

# def test_post_page_comments(client):
#     response = client.get(url_for('post', index=0))
#     assert "Комментарии" in response.data.decode('utf-8')
#     assert "Оставьте комменатрий" in response.data.decode('utf-8')

# def test_about_page(client):
#     response = client.get(url_for('about'))
#     assert response.status_code == 200
#     assert "Об авторе" in response.data.decode('utf-8')

# def test_about_page_content(client):
#     response = client.get(url_for('about'))
#     assert "Lorem ipsum" in response.data.decode('utf-8')

# def test_about_page_image(client):
#     response = client.get(url_for('about'))
#     assert '<img class="avatar"' in response.data.decode('utf-8')

# def test_nonexistent_post(client):
#     response = client.get(url_for('post', index=999))
#     assert response.status_code == 404

# def test_posts_list_length(client):
#     response = client.get(url_for('posts'))
#     assert "Заголовок поста" in response.data.decode('utf-8')
#     # Проверка количества постов
#     assert response.data.decode('utf-8').count("Заголовок поста") == 5

# def test_post_author(client):
#     response = client.get(url_for('post', index=0))
#     assert "Автор:" in response.data.decode('utf-8')

# def test_post_text(client):
#     response = client.get(url_for('post', index=0))
#     assert "Lorem ipsum" in response.data.decode('utf-8')  # Проверка наличия текста поста

# def test_post_comments(client):
#     response = client.get(url_for('post', index=0))
#     assert "Комментарии" in response.data.decode('utf-8')
#     assert "Оставьте комменатрий" in response.data.decode('utf-8')