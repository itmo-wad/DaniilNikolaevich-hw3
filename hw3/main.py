import hashlib
import os
import uuid

from flask import Flask, render_template, redirect, make_response, request, send_from_directory
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename
from waitress import serve
from database_setup import User, Post, session
from decorators import authenticate
from helpers import allowed_posts

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/image/<image_uuid>", methods=["GET"])
@authenticate
def image(user_id, image_uuid, *args, **kwargs):
    if request.method == "GET":
        if image_uuid in [None, "None", "", "default"]:
            return send_from_directory('static/images', "default.jpg")
        return send_from_directory('static/images', f"{image_uuid}.jpg")


@app.route("/posts", methods=["POST", "GET"])
@authenticate
def posts(user_id, *args, **kwargs):
    if request.method == "GET":
        return render_template("posts.html", posts=allowed_posts(user_id), user_id=user_id)
    else:
        if not user_id:
            return redirect("/login")

        data = request.form
        title = data.get("title")
        content = data.get("content")
        is_private = data.get("is_private")
        is_private = True if is_private == "True" else False
        file = request.files['file']
        filename = str(uuid.uuid4())
        if not file:
            filename = "default"
        else:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.jpg"))

        new_post = Post(title=title, content=content, is_private=is_private, author_id=user_id, image_uuid=filename)
        session.add(new_post)
        return render_template("posts.html", posts=allowed_posts(user_id), user_id=user_id)


@app.route("/")
@authenticate
def root(user_id, *args, **kwargs):
    return redirect("/posts")


@app.route("/login")
def login(*args, **kwargs):
    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register(*args, **kwargs):
    if request.method == "GET":
        return render_template("register.html")
    else:
        data = request.form
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        surname = data.get("surname")
        password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()

        result = session.query(User).where(User.email == email).all()
        if result:
            return render_template("error.html", error="You can't use this email, choose another one")

        if not any([email, password, name, surname]):
            return render_template("error.html", error="Data for registration is not full")

        token = str(uuid.uuid4())
        new_user = User(name=name, surname=surname, password=password_hash, email=email, token=token)
        session.add(new_user)

        resp = make_response(redirect("/posts"))
        resp.set_cookie("token", token)
        return resp


@app.route("/auth", methods=['POST'])
def auth(*args, **kwargs):
    data = request.form
    email = data.get("email")
    password = data.get("password")
    password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    if not email or not password:
        return render_template("error.html", error="Email or Password is absent")

    result = session.query(User).where(User.email == email, User.password == password_hash).all()

    if not result:
        return render_template("error.html", error="Invalid Email or Password")
    else:
        resp = make_response(redirect("/posts"))
        resp.set_cookie("token", result[0].token)
        return resp


@app.route("/logout")
def logout(*args, **kwargs):
    resp = make_response(redirect("/login"))
    resp.set_cookie("token", "")
    return resp


if __name__ == "__main__":
    print("Launched!")
    serve(app, host="0.0.0.0", port=5001)
