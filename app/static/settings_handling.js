function addIncentiveToDOM(added) {
    const contenedor = document.getElementById("incentivos_ul")
    const mensajeVacio = document.getElementById("no_incentives")
    if (mensajeVacio) mensajeVacio.remove()

    const nuevoIncentivo = document.createElement("li")
    nuevoIncentivo.setAttribute("data-id", added.id)

    nuevoIncentivo.innerHTML = `
        <div class="d-flex justify-content-start gap-2 align-content-center">
            <div>${added.incentivo}</div>
            <iconify-icon class="cursor-pointer" icon="ic:baseline-delete" width="20" height="20" 
                onclick="handleDeleteIncentive(${added.estudiante_id}, ${added.id})">
            </iconify-icon>
        </div>
    `
    
    contenedor.appendChild(nuevoIncentivo)
    
    document.getElementById("monto").value = ""
}

async function handleAddIncentive(estudianteId, monto, nota, simbolo, moneda) {
    try {
        const added = await addIncentive(estudianteId, monto, nota, simbolo, moneda)
        addIncentiveToDOM(added)

    } catch (error) {
        console.error("Error adding incentive:", error)
    }
}

function removeIncentiveFromDOM(incentive_id) {
    const li = document.querySelector(`#incentivos_ul li[data-id='${incentive_id}']`)
    if (li) li.remove()

    const contenedor = document.getElementById("incentivos_ul")
    if (contenedor.children.length === 0) {
        const mensaje = document.createElement("li")
        mensaje.id = "no_incentives"
        mensaje.textContent = "There is no incentives yet."
        contenedor.appendChild(mensaje)
    }
}

async function handleDeleteIncentive(estudiante_id, incentive_id) {
    try {
        const deletedId = await deleteIncentive(estudiante_id, incentive_id)
        removeIncentiveFromDOM(deletedId)

    } catch (error) {
        console.error("Error deleting incentive:", error)
    }
}

function addRestrictionToDOM(added) {
    const contenedor = document.getElementById("restricciones_ul")
    const mensajeVacio = document.getElementById("no_restrictions")
    if (mensajeVacio) mensajeVacio.remove()

    const nuevaRestriccion = document.createElement("li")
    nuevaRestriccion.setAttribute("data-id", added.id)

    nuevaRestriccion.innerHTML = `
        <div class="d-flex justify-content-start gap-2 align-content-center">
            <div>${added.restriccion}</div>
            <iconify-icon class="cursor-pointer" icon="ic:baseline-delete" width="20" height="20" 
                onclick="handleRemoveRestriction(${added.estudiante_id}, ${added.id})">
            </iconify-icon>
        </div>
    `

    contenedor.appendChild(nuevaRestriccion)

    document.getElementById("restriccion_input").value = ""
}

async function handleAddRestriction(estudianteId, mensaje) {
    try {
        const added = await addRestriction(estudianteId, mensaje)
        addRestrictionToDOM(added)

    } catch (error) {
        console.error("Error adding restriction", error)
    }
}

function removeRestrictionFromDOM(restriction_id) {
    const li = document.querySelector(`#restricciones_ul li[data-id='${restriction_id}']`)
    if (li) li.remove()

    const contenedor = document.getElementById("restricciones_ul")
    if (contenedor.children.length === 0) {
        const mensaje = document.createElement("li")
        mensaje.id = "no_restrictions"
        mensaje.textContent = "There is no restrictions yet."
        contenedor.appendChild(mensaje)
    }
}

async function handleRemoveRestriction(estudiante_id, restriction_id) {
    try {
        const removedId = await deleteRestriction(estudiante_id, restriction_id)
        removeRestrictionFromDOM(removedId)

    } catch (error) {
        console.error("Error removing restriction", error)
    }
}
