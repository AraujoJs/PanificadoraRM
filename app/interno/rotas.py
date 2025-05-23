# coding: UTF-8
"""
Script: Panificadora-RM/rotas
Création: jojo, le 07/05/2025
"""
# Imports
import locale

from app.interno.services import *

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

from flask import Blueprint, redirect, url_for, render_template, request

interno = Blueprint('interno', __name__, template_folder='templates')


@interno.route('/')
def home():
    return redirect(url_for('interno.compras'))


@interno.route('/compras')
def compras():
    filtro = request.args.get("filtro")
    compras = get_todas_compras()
    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras)
    }
    if filtro == "fornecedor":
        context["fornecedores"] = get_todos_fornecedores()
        context["fornecedor_selected"] = True
    elif filtro == "produto":
        context["produtos"] = get_todos_produtos()
        context["produto_selected"] = True
    elif filtro == "periodo":
        anos_disponiveis = get_anos_disponiveis(context["itens"])
        context["anos"] = anos_disponiveis
        context["ano_selected"] = True
        context["mes_selected"] = None
    return render_template("interno.html", **context)


@interno.route('/compras/add', methods=["GET", "POST"])
def compras_add():
    if request.method == "GET":
        de = request.args.get('de')
        produto_id = request.args.get('id')
        if produto_id:
            produto = get_produto(int(produto_id))
        else:
            produto = None
        context = {
            "mode": "add",
            "produtos": get_todos_produtos(),
            "produto_selected": produto
        }
        return render_template('compras_add.html', **context)

    produto_id = request.form['produto_id']
    data_compra = request.form['data_compra']
    data_vencimento = request.form['data_vencimento']
    quantidade = request.form['quantidade']
    preco_total = request.form['preco_total']
    context = {
        "produto_id": produto_id,
        "data_compra": data_compra,
        "data_vencimento": data_vencimento,
        "quantidade": quantidade,
        "preco_total": preco_total,
    }
    sucesso = adicionar_compra(**context)
    if sucesso:
        return redirect(url_for('interno.compras'))
    else:
        context = {
            "mode": "add",
            "produtos": get_todos_produtos(),
            "error": True
        }
        return render_template(**context)


@interno.route('/compras/delete/<int:compra_id>')
def compras_delete(compra_id):
    sucesso = delete_compra(compra_id)

    if not sucesso:
        flash(f"Erro ao deletar compra!")
    return redirect(url_for('interno.compras'))


@interno.route('/compras/update/<int:compra_id>', methods=['GET', 'POST'])
def compras_update(compra_id):
    if request.method == 'GET':
        compra = get_compra(compra_id)
        if compra:
            context = {
                "mode": "update",
                "compra_id": compra_id,
                "produtos": get_todos_produtos(),
                "data_compra": compra.data_compra,
                "data_vencimento": compra.validade,
                "product_selected": compra.produto_id,
                "quantidade": compra.quantidade,
                "preco_total": compra.preco_total
            }
            return render_template('compras_add.html', **context)
        flash("Compra inexistente!")
    elif request.method == 'POST':
        context = {
            "compra_id": request.form['compra_id'],
            "produto_id": request.form['produto_id'],
            "data_compra": request.form['data_compra'],
            "vencimento": request.form['data_vencimento'],
            "quantidade": request.form['quantidade'],
            "preco_total": request.form['preco_total']
        }
        sucesso = update_compra(**context)
        if not sucesso:
            flash("Falha ao atualizar venda.")
        return redirect(url_for('interno.compras'))


@interno.route('/compras/fornecedor/<id>')
def compras_por_fornecedor(id):
    fornecedor = get_fornecedor(id)
    if fornecedor:
        compras = get_compras_fornecedor(fornecedor.id)
        context = {
            "tela": "compras",
            "itens": compras,
            "total": calcular_total(compras),
            "fornecedores": get_todos_fornecedores(),
            "fornecedor_selected": fornecedor
        }
        return render_template('interno.html', **context)
    return redirect(url_for("interno.compras"))


@interno.route('/compras/produtos/<produto_id>')
def compras_por_produto(produto_id):
    produto = get_produto(produto_id)
    if produto:
        compras = get_compras_produto(produto_id)
        context = {
            "tela": "compras",
            "itens": compras,
            "total": calcular_total(compras),
            "produtos": get_todos_produtos(),
            "produto_selected": produto
        }
        return render_template('interno.html', **context)
    return redirect(url_for("interno.compras"))


@interno.route('/compras/produtos/add')
def add_produto_view():
    is_redirected = request.args.get('de')
    fornecedor_id = request.args.get('id')
    if fornecedor_id:
        fornecedor_selected = get_fornecedor(int(fornecedor_id))
    else:
        fornecedor_selected = None
    context = {
        'from': is_redirected,
        'mode': 'add',
        'fornecedores': get_todos_fornecedores(),
        'fornecedor_selected': fornecedor_selected,
        'tipos': get_tipos_produtos()
    }
    return render_template('produtos_add.html', **context)

@interno.route('/compras/produtos/add', methods=['POST'])
def add_produto():
    is_redirected = request.form['from']
    fornecedor_id = request.form['fornecedor_id']
    fornecedor = get_fornecedor(int(fornecedor_id))

    nome = request.form['nome']
    tipo = get_tipo_produto(int(request.form['tipo_id']))


    context = {
        "fornecedor": fornecedor,
        "nome": nome,
        "tipo": tipo
    }

    produto = adicionar_produto(**context)
    if produto:
        if is_redirected:
            url = get_url_para(is_redirected, produto.id)
            return redirect(url)
    redirect(url_for('interno.compras'))

@interno.route('/compras/fornecedor/add', methods=['GET'])
def add_fornecedor_view():
    is_redirected = request.args.get('from')

    context = {
        'from': is_redirected,
        'mode': 'add',
        'categorias': get_todas_categorias()
    }
    return render_template('fornecedores_add.html', **context)

@interno.route('/compras/fornecedor/add', methods=['POST'])
def add_fornecedor():
    is_redirected = request.form['from']
    nome = request.form['nome']
    contato = request.form['contato']
    categoria = request.form['categoria']

    context = {
        'nome': nome,
        'contato': contato,
        'categoria': categoria,
    }
    fornecedor = adicionar_fornecedor(**context)
    if fornecedor:
        if is_redirected:
            url = get_url_para(is_redirected, fornecedor.id)
            return redirect(url)
    return render_template('fornecedores_add.html', **context)




def get_url_para(is_redirected, id):
    """Compra, produto"""
    if is_redirected == 'compras':
        return url_for('interno.compras_add', id=id, de="produtos")
    elif is_redirected == 'produtos':
        return url_for('interno.add_produto_view', id=id, de="fornecedor")
    elif is_redirected == 'fornecedor':
        return url_for('interno.compras_add', id=id, de="produtos")
    else:
        return url_for('interno.compras')

@interno.route('/compras/periodo/<ano>')
def compras_periodo_ano(ano):
    if not ano_valido(ano):
        return redirect(url_for("interno.compras"))
    compras = get_compras_ano(ano)
    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "anos": get_anos_disponiveis(compras),
        "ano_selected": int(ano),
        "meses": get_meses_disponiveis(ano)
    }
    return render_template('interno.html', **context)


@interno.route('/compras/periodo/<ano>/<mes>')
def compras_periodo_mes(ano, mes):
    if ano == "all":
        return redirect("interno.compras")
    if mes == "all":
        compras = get_compras_ano(ano)
        mes_selected = "all"
    else:
        if not ano_valido(ano) or not mes_valido(ano, mes):
            return redirect(url_for("interno.compras"))
        compras = get_compras_mes(ano, mes)
        mes_selected = int(mes)
    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "anos": get_anos_disponiveis(compras),
        "meses": get_meses_disponiveis(ano),
        "ano_selected": int(ano),
        "mes_selected": mes_selected
    }
    return render_template('interno.html', **context)


@interno.route('/produtos')
def produtos():
    context = {
        "tela": "produtos",
        "itens": get_todos_produtos()
    }
    return render_template('interno.html', **context)


@interno.route('/fornecedores')
def fornecedores():
    context = {
        "tela": "fornecedores",
        "itens": get_todos_fornecedores()
    }
    return render_template('interno.html', **context)


@interno.route('/relatorio')
def relatorio():
    return render_template('relatorios_interno.html')
