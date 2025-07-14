# coding: UTF-8
"""
Script: Panificadora-RM/rotas
Création: jojo, le 07/05/2025
"""
# Imports
import locale

from app.interno.services import *


from flask import Blueprint, redirect, url_for, render_template, request

interno = Blueprint('interno', __name__, template_folder='templates')


@interno.route('/')
def home():
    return redirect(url_for('interno.compras'))


@interno.route('/compras')
def compras():
    filtro = request.args.get("filtro")
    fornecedor_id = request.args.get("fornecedor_id")
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', "asc")

    compras = get_todas_compras()

    if filtro == "fornecedor" and fornecedor_id:
        compras = [c for c in compras_por_fornecedor(str(fornecedor_id))]

    reverse = order == "desc"
    if sort == "id":
        compras.sort(key=lambda x: x.id, reverse=reverse)
    elif sort == "produto":
        compras.sort(key=lambda x: x.produto.nome.lower(), reverse=reverse)
    elif sort == "data":
        compras.sort(key=lambda x: x.data_compra, reverse=reverse)
    elif sort == "validade":
        compras.sort(key=lambda x: x.validade, reverse=reverse)
    elif sort == "quantidade":
        compras.sort(key=lambda x: x.quantidade, reverse=reverse)
    elif sort == "preco_total":
        compras.sort(key=lambda x: x.preco_total, reverse=reverse)

    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "sort": sort,
        "order": order,
        "fornecedor_id": fornecedor_id
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


@interno.route('/compras/consumir/<int:compra_id>', methods=['POST'])
def compras_consumir(compra_id):
    consumir_compra(compra_id)
    return redirect(url_for('interno.relatorio'))


@interno.route('/compras/add', methods=["GET", "POST"])
def compras_add():
    if request.method == "GET":
        de = request.args.get('from')
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

    produto_id = request.form.get('produto_id')
    data_compra = request.form.get('data_compra')
    data_vencimento = request.form.get('data_vencimento')
    quantidade = request.form.get('quantidade')
    preco_total = request.form.get('preco_total')

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


@interno.route('/compras/produtos/delete/<int:produto_id>')
def produto_delete(produto_id):
    sucesso = desativar_produto(produto_id)

    if not sucesso:
        flash(f"Erro ao desativar produto!")
    return redirect(url_for('interno.produtos'))


@interno.route('/compras/fornecedores/delete/<int:fornecedor_id>')
def fornecedor_delete(fornecedor_id):
    sucesso = desativar_fornecedor(fornecedor_id)

    if not sucesso:
        flash(f"Erro ao desativar produto!")
    return redirect(url_for('interno.fornecedores'))


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


@interno.route('/compras/produtos/update/<int:produto_id>', methods=['GET', 'POST'])
def produto_update(produto_id):
    if request.method == 'GET':
        produto = get_produto(produto_id)
        if produto:
            context = {
                "mode": "update",
                "produto_id": produto_id,
                "produto": produto,
                "fornecedores": get_todos_fornecedores(),
                "tipos": get_tipos_produtos(),
                "fornecedor_selected": get_fornecedor(produto.fornecedor_id),
                "tipo_selected": get_tipo_id(produto.tipo)
            }
            return render_template('produtos_add.html', **context)
        flash("Compra inexistente!")
    elif request.method == 'POST':
        context = {
            "produto_id": request.form['produto_id'],
            "fornecedor_id": request.form['fornecedor_id'],
            "nome": request.form['nome'],
            "tipo_id": request.form['tipo_id']
        }
        sucesso = update_produto(**context)
        if not sucesso:
            flash("Falha ao atualizar produto.")
        return redirect(url_for('interno.produtos'))


@interno.route('/compras/fornecedores/update/<int:fornecedor_id>', methods=['GET', 'POST'])
def fornecedor_update(fornecedor_id):
    if request.method == 'GET':
        fornecedor = get_fornecedor(fornecedor_id)
        if fornecedor:
            context = {
                "mode": "update",
                "categorias": get_todas_categorias(),
                "fornecedor": fornecedor
            }
            return render_template('fornecedores_add.html', **context)
        flash("Compra inexistente!")
    elif request.method == 'POST':
        categoria = get_categoria(request.form['categoria'])
        context = {
            "fornecedor_id": request.form['fornecedor_id'],
            "nome": request.form['nome'],
            "contato": request.form['contato'],
            "categoria": categoria
        }
        sucesso = update_fornecedor(**context)
        if not sucesso:
            flash("Falha ao atualizar fornecedor.")
        return redirect(url_for('interno.fornecedores'))


@interno.route('/compras/fornecedor/<int:id>')
def compras_por_fornecedor(id):
    fornecedor = get_fornecedor(id)
    if not fornecedor:
        return redirect(url_for("interno.compras"))

    compras = get_compras_fornecedor(fornecedor.id)

    # 🟨 Pega os parâmetros de ordenação
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    reverse = order == "desc"

    # 🟩 Aplica ordenação
    if sort == "id":
        compras.sort(key=lambda x: x.id, reverse=reverse)
    elif sort == "produto":
        compras.sort(key=lambda x: x.produto.nome.lower(), reverse=reverse)
    elif sort == "data":
        compras.sort(key=lambda x: x.data_compra, reverse=reverse)
    elif sort == "validade":
        compras.sort(key=lambda x: x.validade, reverse=reverse)
    elif sort == "quantidade":
        compras.sort(key=lambda x: x.quantidade, reverse=reverse)
    elif sort == "preco_total":
        compras.sort(key=lambda x: x.preco_total, reverse=reverse)

    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "fornecedores": get_todos_fornecedores(),
        "fornecedor_selected": fornecedor,
        "sort": sort,
        "order": order,
        "filtro": "fornecedor",  # <- Adiciona isso
        "filtro_id": fornecedor.id  # <- E isso também
    }
    return render_template('interno.html', **context)


@interno.route('/compras/produtos/<produto_id>')
def compras_por_produto(produto_id):
    produto = get_produto(produto_id)
    if produto:
        compras = get_compras_produto(produto_id)

        sort = request.args.get('sort', 'id')
        order = request.args.get('order', 'asc')
        reverse = order == "desc"

        # Ordena conforme coluna e ordem
        if sort == "id":
            compras.sort(key=lambda x: x.id, reverse=reverse)
        elif sort == "produto":
            compras.sort(key=lambda x: x.produto.nome.lower(), reverse=reverse)
        elif sort == "data":
            compras.sort(key=lambda x: x.data_compra, reverse=reverse)
        elif sort == "validade":
            compras.sort(key=lambda x: x.validade, reverse=reverse)
        elif sort == "quantidade":
            compras.sort(key=lambda x: x.quantidade, reverse=reverse)
        elif sort == "preco_total":
            compras.sort(key=lambda x: x.preco_total, reverse=reverse)

        context = {
            "tela": "compras",
            "itens": compras,
            "total": calcular_total(compras),
            "produtos": get_todos_produtos(),
            "produto_selected": produto,
            "filtro": "produto",
            "filtro_id": produto_id,
            "produto_selected": produto,
            "sort": request.args.get('sort', 'id'),
            "order": request.args.get('order', 'asc')
        }
        return render_template('interno.html', **context)
    return redirect(url_for("interno.compras"))


@interno.route('/compras/produtos/add')
def add_produto_view():
    endpoint = request.args.get('end_point')
    fornecedor_selected = get_fornecedor(request.args.get('id'))

    if (endpoint == "produtos") or (endpoint == "compras"):
        context = {
            'endpoint': endpoint,
            'mode': 'add',
            'fornecedores': get_todos_fornecedores(),
            'fornecedor_selected': fornecedor_selected,
            'tipos': get_tipos_produtos()
        }
        return render_template('produtos_add.html', **context)
    else:
        flash("Endpoint desconhecido!")


@interno.route('/compras/produtos/add', methods=['POST'])
def add_produto():
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
        endpoint = request.form.get('endpoint')

        if endpoint == 'produtos':
            url = url_for('interno.produtos')
            return redirect(url)
        elif endpoint == 'compras':
            url = url_for('interno.compras_add', id=produto.id)
            return redirect(url)

    flash("Falha ao adicionar produto!")
    return redirect(url_for('interno.produtos'))


@interno.route('/compras/fornecedor/add', methods=['GET'])
def add_fornecedor_view():
    endpoint = request.args.get('end_point')

    context = {
        'endpoint': endpoint,
        'mode': 'add',
        'categorias': get_todas_categorias()
    }
    return render_template('fornecedores_add.html', **context)


@interno.route('/compras/fornecedor/add', methods=['POST'])
def add_fornecedor():
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
        endpoint = request.form.get('endpoint')

        if (endpoint == 'produtos') or (endpoint == 'compras'):
            url = url_for('interno.add_produto_view', end_point=endpoint, id=fornecedor.id)
            return redirect(url)
        else:
            url = url_for('interno.fornecedores')
            return redirect(url)

    flash("Falha ao adicionar fornecedor!")
    return redirect(url_for('interno.fornecedores'))


@interno.route('/compras/periodo/<ano>')
def compras_periodo_ano(ano):
    if not ano_valido(ano):
        return redirect(url_for("interno.compras"))
    compras = get_compras_ano(ano)

    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    reverse = order == 'desc'

    if sort == "id":
        compras.sort(key=lambda x: x.id, reverse=reverse)
    elif sort == "produto":
        compras.sort(key=lambda x: x.produto.nome.lower(), reverse=reverse)
    elif sort == "data":
        compras.sort(key=lambda x: x.data_compra, reverse=reverse)
    elif sort == "validade":
        compras.sort(key=lambda x: x.validade, reverse=reverse)
    elif sort == "quantidade":
        compras.sort(key=lambda x: x.quantidade, reverse=reverse)
    elif sort == "preco_total":
        compras.sort(key=lambda x: x.preco_total, reverse=reverse)

    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "anos": get_anos_disponiveis(compras),
        "ano_selected": int(ano),
        "meses": get_meses_disponiveis(ano),
        "filtro": "periodo",  # filtro ativo
        "filtro_id": int(ano),  # identificador para o filtro (ano)
        "fornecedor_selected": None,  # garantir consistência no contexto
        "produto_selected": None,
        "sort": request.args.get('sort', 'id'),
        "order": request.args.get('order', 'asc')
    }
    return render_template('interno.html', **context)


@interno.route('/compras/periodo/<ano>/<mes>')
def compras_periodo_mes(ano, mes):
    if ano == "all":
        return redirect(url_for("interno.compras"))
    if mes == "all":
        compras = get_compras_ano(ano)
        mes_selected = "all"
    else:
        if not ano_valido(ano) or not mes_valido(ano, mes):
            return redirect(url_for("interno.compras"))
        compras = get_compras_mes(ano, mes)
        mes_selected = int(mes)

    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    reverse = order == 'desc'

    if sort == "id":
        compras.sort(key=lambda x: x.id, reverse=reverse)
    elif sort == "produto":
        compras.sort(key=lambda x: x.produto.nome.lower(), reverse=reverse)
    elif sort == "data":
        compras.sort(key=lambda x: x.data_compra, reverse=reverse)
    elif sort == "validade":
        compras.sort(key=lambda x: x.validade, reverse=reverse)
    elif sort == "quantidade":
        compras.sort(key=lambda x: x.quantidade, reverse=reverse)
    elif sort == "preco_total":
        compras.sort(key=lambda x: x.preco_total, reverse=reverse)

    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "anos": get_anos_disponiveis(compras),
        "meses": get_meses_disponiveis(ano),
        "ano_selected": int(ano),
        "mes_selected": mes_selected,
        "filtro": "periodo",
        "filtro_id": (int(mes) if mes != "all" else "all"),  # para diferenciar filtro ativo
        "fornecedor_selected": None,
        "produto_selected": None,
        "sort": request.args.get('sort', 'id'),
        "order": request.args.get('order', 'asc')
    }
    return render_template('interno.html', **context)


@interno.route('/produtos')
def produtos():
    ordenar = request.args.get("ordenar", "id")
    ordem = request.args.get("ordem", "asc")

    produtos = get_todos_produtos()
    produtos = [p for p in produtos if p.ativo]

    # Aplica ordenação
    reverse = ordem == "desc"
    try:
        if ordenar == "fornecedor":
            produtos = sorted(produtos, key=lambda x: x.fornecedor.nome, reverse=reverse)
        else:
            produtos = sorted(produtos, key=lambda x: getattr(x, ordenar), reverse=reverse)

    except AttributeError:
        pass  # caso a coluna não exista, não ordena

    context = {
        "tela": "produtos",
        "itens": produtos,
        "ordenar": ordenar,
        "ordem": ordem
    }
    return render_template('interno.html', **context)


@interno.route('/fornecedores')
def fornecedores():
    ordenar = request.args.get("ordenar", default="id")
    ordem = request.args.get("ordem", default="asc")

    fornecedores = get_todos_fornecedores()

    reverse = ordem == "desc"
    if ordenar == "id":
        fornecedores.sort(key=lambda x: x.id, reverse=reverse)
    elif ordenar == "nome":
        fornecedores.sort(key=lambda x: x.nome.lower(), reverse=reverse)
    elif ordenar == "contato":
        fornecedores.sort(key=lambda x: x.contato.lower(), reverse=reverse)
    elif ordenar == "categoria":
        fornecedores.sort(key=lambda x: x.categoria.lower(), reverse=reverse)

    context = {
        "tela": "fornecedores",
        "itens": fornecedores,
        "ordenar": ordenar,
        "ordem": ordem
    }
    return render_template('interno.html', **context)


@interno.route('/relatorio')
def relatorio():
    anos = request.args.get('ano')
    meses = request.args.get('mes')

    today = request.args.get('today')

    if today:
        anos = get_anos_disponiveis(compras=None)
        meses = get_meses_disponiveis(anos[0])[-1][0]


    compras = get_todas_compras()
    if len(compras) == 0:
        context = {
            "compras": None,
            "compras_vencimento": None,
            "total": 0,
            "anos": [anos],
            "meses": get_meses_disponiveis(anos[0]),
            "ano_selected": get_atual_ano_mes(compras=None)["anos"],
            "mes_selected": get_atual_ano_mes(compras=None)["mes"],
            "fornecedores": None,
            "produtos": None
        }

        return render_template('relatorios_interno.html', **context)

    total = get_total_compras(compras)
    anos_disponiveis = get_anos_disponiveis(compras)
    meses_disponiveis = get_meses_disponiveis('all')

    ano_mes = get_atual_ano_mes(compras)

    if not anos:
        anos = 'all'
    if not meses:
        meses = None

    if anos == 'all':
        ano_selected = 'all'
        meses_disponiveis = get_meses_disponiveis('all')
    else:
        ano_selected = int(anos[0])
        meses_disponiveis = get_meses_disponiveis(anos[0])
        compras = get_compras_ano(ano_selected)

    if meses == 'all':
        mes_selected = 'all'
    else:
        if meses:
            mes_selected = int(meses)
            compras = get_compras_mes(anos[0], meses)

    if anos == 'all' or meses == 'all':
        sort = request.args.get('sort', 'id')
        order = request.args.get('order', 'asc')
        meses_disponiveis = get_meses_disponiveis('all')

        sort = request.args.get('sort', 'id')
        order = request.args.get('order', 'asc')
        reverse = order == 'desc'
        if sort == 'produto':
            compras.sort(key=lambda c: c.produto.nome.lower() if c.produto else '', reverse=reverse)
        elif sort == 'data':
            compras.sort(key=lambda c: c.data_compra, reverse=reverse)
        elif sort == 'validade':
            compras.sort(key=lambda c: c.validade or datetime.max.date(), reverse=reverse)
        elif sort == 'quantidade':
            compras.sort(key=lambda c: c.quantidade, reverse=reverse)
        elif sort == 'preco_total':
            compras.sort(key=lambda c: c.preco_total, reverse=reverse)
        else:
            compras.sort(key=lambda c: c.id, reverse=reverse)

        total = get_total_compras(compras)
        if anos == 'all':
            ano_selected = 'all'
        else:
            ano_selected = int(anos)

        fornecedores = get_todos_fornecedores()
        produtos = get_todos_produtos()

        context = {
            "compras": compras,
            "compras_vencimento": compras_por_vencimento(compras),
            "total": total,
            "anos": anos_disponiveis,
            "meses": meses_disponiveis,
            "sort": sort,
            "order": order,
            "ano_selected": ano_selected,
            "mes_selected": meses,
            "fornecedores": fornecedores,
            "produtos": produtos
        }
        return render_template('relatorios_interno.html', **context)

    if anos and anos != 'all':
        compras = [c for c in compras if c.data_compra.year == int(anos[0])]
    if meses and meses != 'all':
        compras = [c for c in compras if c.data_compra.month == int(meses)]
    total = get_total_compras(compras)
    anos = get_anos_disponiveis(compras)

    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    reverse = order == 'desc'
    if sort == 'produto':
        compras.sort(key=lambda c: c.produto.nome.lower() if c.produto else '', reverse=reverse)
    elif sort == 'data':
        compras.sort(key=lambda c: c.data_compra, reverse=reverse)
    elif sort == 'validade':
        compras.sort(key=lambda c: c.validade or datetime.max.date(), reverse=reverse)
    elif sort == 'quantidade':
        compras.sort(key=lambda c: c.quantidade, reverse=reverse)
    elif sort == 'preco_total':
        compras.sort(key=lambda c: c.preco_total, reverse=reverse)
    else:
        compras.sort(key=lambda c: c.id, reverse=reverse)

    fornecedores = get_todos_fornecedores()
    produtos = get_todos_produtos()

    context = {
        "compras": compras,
        "compras_vencimento": compras_por_vencimento(compras),
        "total": total,
        "anos": anos_disponiveis,
        "meses": meses_disponiveis,
        "sort": sort,
        "order": order,
        "ano_selected": ano_selected,
        "mes_selected": mes_selected,
        "fornecedores": fornecedores,
        "produtos": produtos
    }

    return render_template('relatorios_interno.html', **context)


@interno.route('/relatorio/<ano>')
def relatorio_ano(ano):
    compras = get_compras_ano(int(ano))
    total = get_total_compras(compras)

    anos = get_anos_disponiveis(get_todas_compras())
    meses = get_meses_disponiveis(ano)

    fornecedores = get_todos_fornecedores()
    produtos = get_todos_produtos()

    context = {
        "compras": compras,
        "compras_vencimento": compras_por_vencimento(compras),
        "total": total,
        "anos": anos,
        "meses": meses,
        "ano_selected": int(ano),
        "mes_selected": 'all',
        "fornecedores": fornecedores,
        "produtos": produtos
    }
    return render_template('relatorios_interno.html', **context)


@interno.route('/relatorio/<ano>/<mes>')
def relatorio_ano_mes(ano, mes):
    if mes == 'all' or ano == 'all':
        return redirect(url_for('interno.relatorio', ano='all', mes='all'))

    elif ano and mes:
        compras = get_compras_mes(int(ano), int(mes))
        total = get_total_compras(compras)
        anos = get_anos_disponiveis(get_todas_compras())

        fornecedores = get_todos_fornecedores()
        produtos = get_todos_produtos()

        meses = get_meses_disponiveis(ano)
        context = {
            "compras": compras,
            "compras_vencimento": compras_por_vencimento(compras),
            "total": total,
            "anos": anos,
            "meses": meses,
            "ano_selected": int(ano),
            "mes_selected": int(mes),
            "fornecedores": fornecedores,
            "produtos": produtos
        }
        return render_template('relatorios_interno.html', **context)

    else:
        return redirect(url_for('interno.relatorio'))


def compras_por_vencimento(compras):
    return sorted(
        compras,
        key=lambda c: (c.dias_para_vencimento if c.dias_para_vencimento is not None else float('inf'))
    )


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
