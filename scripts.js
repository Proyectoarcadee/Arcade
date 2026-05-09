window.onload = () => {
    const user = localStorage.getItem('usuario'); 
    const planActivo = localStorage.getItem('plan_gaymer'); // Ejemplo: "ESENCIAL", "PRO", "GAYMER"

    if (!user) {
        window.location.href = 'login.html';
        return;
    }

    // Mostrar el nombre de usuario y su plan actual
    const nombreUsuario = user.toUpperCase();
    const etiquetaPlan = planActivo ? ` | PLAN: ${planActivo}` : " | PLAN: GRATUITO"; 
    document.getElementById('user-display').innerText = nombreUsuario + etiquetaPlan; 

    if (typeof listaDeJuegos !== 'undefined') {
        let juegosFiltrados = [];

        // Filtro estricto por nombres: ESENCIAL, PRO, GAYMER
        if (planActivo === 'ESENCIAL') {
            juegosFiltrados = listaDeJuegos.slice(0, 20); 
        } else if (planActivo === 'PRO') {
            juegosFiltrados = listaDeJuegos.slice(0, 25); 
        } else if (planActivo === 'GAYMER') {
            juegosFiltrados = listaDeJuegos.slice(0, 30); 
        } else {
            // Usuario sin plan o con nivel base
            juegosFiltrados = listaDeJuegos.slice(0, 15); 
        }
        
        renderizarGrid(juegosFiltrados);
    }
};

function renderizarGrid(lista) {
    const contenedor = document.getElementById('grid');
    if (!contenedor) return;

    contenedor.innerHTML = ''; 

    lista.forEach(juego => {
        contenedor.innerHTML += `
            <div class="card-juego">
                <img src="${juego.imagen}" alt="${juego.titulo}" 
                     onerror="this.src='https://via.placeholder.com/250x200?text=Error+Imagen'">
                <div class="info-juego">
                    <h3>${juego.titulo}</h3>
                    <span class="badge-consola">${juego.consola.toUpperCase()}</span>
                    <button class="btn-instalar" onclick="window.location.href='${juego.url}'">
                        INSTALAR
                    </button>
                </div>
            </div>`;
    });
}