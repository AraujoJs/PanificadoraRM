document.addEventListener("DOMContentLoaded", function () {
    const filtroSelect = document.getElementById('filtro');
    const fornecedorSelect = document.getElementById('fornecedor');
    const produtoSelect = document.getElementById('produto');
    const periodoAnoSelect = document.getElementById('periodo-ano');
    const periodoMesSelect = document.getElementById('periodo-mes');

    if (filtroSelect) {
        filtroSelect.addEventListener('change', function () {
            document.getElementById('fornecedor-filter').style.display = 'none';
            document.getElementById('produto-filter').style.display = 'none';
            document.getElementById('data-filter').style.display = 'none';
            document.getElementById('data-ano-filter').style.display = 'none';

            const filtro = filtroSelect.value;

            if (filtro === "all") {
                window.location.href = `/interno/compras`
            } else {
                window.location.href = `/interno/compras?filtro=${filtro}`;
            }
        });
    }

    if (produtoSelect) {
        produtoSelect.addEventListener('change', function () {
            const produtoId = this.value;
            if (produtoId) {
                window.location.href = `/interno/compras/produto/${produtoId}`;
            }
        });
    }

    if (fornecedorSelect) {
        fornecedorSelect.addEventListener('change', function () {
            const fornecedorId = this.value;
            if (fornecedorId) {
                window.location.href = `/interno/compras/fornecedor/${fornecedorId}`;
            }
        });
    }

    if (periodoAnoSelect) {
        periodoAnoSelect.addEventListener('change', function () {
            document.getElementById('data-filter').style.display = 'block';
            const periodoId = this.value;
            window.location.href = `/interno/compras/periodo/${periodoId}`;
        });
    }

    if (periodoMesSelect) {
        periodoMesSelect.addEventListener('change', function () {
            const mes = this.value;
            const ano = document.getElementById('periodo-ano').value;
            window.location.href = `/interno/compras/periodo/${ano}/${mes}`;
        });
    }
});