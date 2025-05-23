from gettext import install

from sqlalchemy.dialects.postgresql import psycopg2

def get_connection():
    return psycopg2.connect(
        host="root",
        database="panificadorarm",
        user="root",
        password="ee9d8823c9eb5b7ea3bdfb2c6502e987",
        cursor_factory=RealDictCursor
    )

from flask import Flask, render_template, make_response
import pdfkit
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="seu_banco",
        user="postgres",
        password="sua_senha",
        cursor_factory=RealDictCursor
    )

@app.route("/relatorio")
def relatorio():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM compras")
            compras = cursor.fetchall()

            cursor.execute("SELECT * FROM fornecedores")
            fornecedores = cursor.fetchall()

            cursor.execute("SELECT * FROM produtos")
            produtos = cursor.fetchall()

    total = sum(c['valor'] for c in compras)

    return render_template("relatorio.html", compras=compras, fornecedores=fornecedores, produtos=produtos, total=total)

@app.route("/gerar-pdf")
def gerar_pdf():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM compras")
            compras = cursor.fetchall()

            cursor.execute("SELECT * FROM fornecedores")
            fornecedores = cursor.fetchall()

            cursor.execute("SELECT * FROM produtos")
            produtos = cursor.fetchall()

    total = sum(c['valor'] for c in compras)

    html = render_template("relatorio.html", compras=compras, fornecedores=fornecedores, produtos=produtos, total=total)
    pdf = pdfkit.from_string(html, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
    return response

if name == "__main__":
    app.run(debug=True)