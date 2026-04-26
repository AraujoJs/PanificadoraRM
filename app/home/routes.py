# coding: UTF-8
from flask import Blueprint, render_template
from utils.auth import token_required

inicio = Blueprint("home_bp", __name__, template_folder="templates")


@inicio.route("/produtos")
@token_required
def products_page(current_user):
    return render_template("product.html")


@inicio.route("/usuarios")
@token_required
def users_page(current_user):
    return render_template("users.html")
