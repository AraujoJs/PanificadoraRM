document.addEventListener("DOMContentLoaded", function () {
    const dataCompra = document.getElementById('data-compra');
    const dataVencimento = document.getElementById('data-vencimento');
    const containerVencimento = document.getElementById('container-vencimento');

    const precoTotalVisor = document.getElementById('preco-total-visor');

    const precoTotal = document.getElementById('preco-total');

    if (dataCompra.value.size === 0) {
        containerVencimento.style.display = 'none';
    } else {
        containerVencimento.style.display = 'inline-block';
    }

    if (dataCompra) {
        dataCompra.addEventListener('change', function () {
            dataVencimento.min = dataCompra.value
            dataVencimento.value = dataCompra.value

            containerVencimento.style.display = "inline-block"
        })
    }

    // Função para formatar número como moeda brasileira
    function formatarMoeda(valor) {
        const numero = parseFloat(valor);
        if (isNaN(numero)) return '';
        return numero.toLocaleString("pt-BR",
            {style: "currency", currency: "BRL"})
    }


    if (precoTotal.value) {
        precoTotalVisor.textContent = `Total: ${formatarMoeda(precoTotal.value)}`;
    }
    precoTotal.addEventListener('change', function () {
        const valor = formatarMoeda(this.value)
        precoTotalVisor.textContent = `Total: ${valor}`
    })

})


