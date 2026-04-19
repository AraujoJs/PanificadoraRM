document.addEventListener("DOMContentLoaded", function () {
    const periodoAnoSelect = document.getElementById('periodo-ano');
    const periodoMesSelect = document.getElementById('periodo-mes');

    const mesFilterContainer = document.getElementById('data-mes-filter');



    if (periodoAnoSelect) {
        periodoAnoSelect.addEventListener('change', function () {
            if (this.value === 'all') {
                mesFilterContainer.style.display = 'none';
                window.location.href = `/interno/relatorio?ano=all`;
            } else {
                mesFilterContainer.style.display = 'block';
                const periodoId = this.value;
                window.location.href = `/interno/relatorio/${periodoId}`;
            }
        });
    }

    if (periodoMesSelect) {
        periodoMesSelect.addEventListener('change', function () {
            const mes = this.value;
            const ano = document.getElementById('periodo-ano').value;

            if (mes === 'all') {
                window.location.href = `/interno/relatorio/${ano}`
            }
            else {
                window.location.href = `/interno/relatorio/${ano}/${mes}`;
            }


        });
    }

});
