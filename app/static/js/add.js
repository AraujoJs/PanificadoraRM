document.addEventListener("DOMContentLoaded", function () {
    const dataCompra = document.getElementById('data-compra');
    const dataVencimento = document.getElementById('data-vencimento');
    const containerVencimento = document.getElementById('container-vencimento');
    const produtoSelect = document.getElementById('produtos');
    const fornecedorSelect = document.getElementById('fornecedores');
    const precoTotalVisor = document.getElementById('preco-total-visor');
    const endpoint = document.getElementById('endpoint')
    const contatoInput = document.getElementById('contato');

    const precoTotal = document.getElementById('preco-total');

    if (contatoInput) {
        IMask(contatoInput, {
            mask: '(00) 00000-0000'
        });
    }

    if (dataCompra) {
        if (dataCompra.value.size === 0) {
            containerVencimento.style.display = 'none';
        } else {
            containerVencimento.style.display = 'inline-block';
        }

        dataCompra.addEventListener('change', function () {
            dataVencimento.min = dataCompra.value
            dataVencimento.value = dataCompra.value

            containerVencimento.style.display = "inline-block"
        })
    }

    if (produtoSelect) {
        produtoSelect.addEventListener('change', function () {
            const produtoId = this.value;

            if (produtoId === 'add') {
                window.location.href = `/interno/compras/produtos/add?end_point=compras`;
            } else if (produtoId) {
                console.log(`Selecionado produto: ${produtoId}`);
                // window.location.href = `/interno/compras/produtos/${produtoId}`;
            }
        });
    }
    if (fornecedorSelect) {
        fornecedorSelect.addEventListener('change', function () {
            const fornecedorId = this.value;

            if (fornecedorId === 'add') {
                window.location.href = `/interno/compras/fornecedor/add?end_point=${endpoint.value}`;
            } else if (fornecedorId) {
                console.log(`Selecionado fornecedor: ${fornecedorId}`);
                // window.location.href = `/interno/compras/produtos/${produtoId}`;
            }
        });
    }

    // Função para formatar número como moeda brasileira
    function formatarMoeda(valor) {
        const numero = parseFloat(valor);
        if (isNaN(numero)) return '';
        return numero.toLocaleString("pt-BR",
            {style: "currency", currency: "BRL"})
    }

if (precoTotal) {
    if (precoTotal.value) {
        precoTotalVisor.textContent = `Total: ${formatarMoeda(precoTotal.value)}`;
    }

    precoTotal.addEventListener('change', function () {
        const valor = formatarMoeda(this.value)
        precoTotalVisor.textContent = `Total: ${valor}`
    });
}
})


