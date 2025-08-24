
const addIncentivoBtn = document.getElementById("add_incentive_btn")

addIncentivoBtn.addEventListener('click', agregarIncentivo)

function agregarIncentivo() {
    const datosInput = crearMensajeIncentivo(...incentiveVars())
    const contenedor = document.getElementById("incentivos_ul")
    const nuevoIncentivo = document.createElement("li")
    nuevoIncentivo.textContent = datosInput

    contenedor.appendChild(nuevoIncentivo)

    const montoInput = document.getElementById("monto")
    montoInput.value = ""
}

function crearMensajeIncentivo(estudianteId, monto, nota, simbolo, moneda) {
    return `${simbolo}${monto} ${moneda} for grades >= ${nota}`
}

