async function deleteRestriction(estudiante_id, restriction_id) {
    try {
        const response = await fetch("/delete_restriction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ estudiante_id: estudiante_id, restriction_id: restriction_id })
        })

        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`)
        
        const li = document.querySelector(`#restricciones_ul li[data-id='${restriction_id}']`)
        if (li) li.remove()

        const contenedor = document.getElementById("restricciones_ul")
        if (contenedor.children.length === 0) {
            const mensaje = document.createElement("li")
            mensaje.id = "no_restrictions"
            mensaje.textContent = "There is no restrictions yet."
            contenedor.appendChild(mensaje)
        }

        const data = await response.json()
        console.log("Respuesta del servidor:", data)
        return data
    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function deleteIncentive(estudiante_id, incentive_id) {
    try {
        const response = await fetch("/delete_incentive", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ estudiante_id: estudiante_id, incentive_id: incentive_id })
        })
        
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`)
        
        const li = document.querySelector(`#incentivos_ul li[data-id='${incentive_id}']`)
        if (li) li.remove()

        const contenedor = document.getElementById("incentivos_ul")
        if (contenedor.children.length === 0) {
            const mensaje = document.createElement("li")
            mensaje.id = "no_incentives"
            mensaje.textContent = "There is no incentives yet."
            contenedor.appendChild(mensaje)
        }
        
        const data = await response.json()
        console.log("Respuesta del servidor:", data)
        return data

    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function addIncentive(estudianteId, monto, nota, simbolo, moneda) {
    try {
        console.log(estudianteId, monto, nota, simbolo, moneda)
        const response = await fetch("/add_incentive", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(
                {
                    estudiante_id: estudianteId,
                    monto: monto,
                    nota: nota,
                    simbolo: simbolo,
                    moneda: moneda
                })
        })

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`)
        }

        const data = await response.json()
        console.log("Respuesta del servidor:", data)
        return data
    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function addRestriction(estudianteId, mensaje) {
    try {
        const response = await fetch("/add_restriction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(
                {
                    estudiante_id: estudianteId,
                    mensaje: mensaje
                })
        })

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`)
        }

        const data = await response.json()
        console.log("Respuesta del servidor:", data)
        return data
    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function fetchCambiarPais(estudianteId, paisId) {
    try {
        const response = await fetch("/change_country", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(
                {
                    estudiante_id: estudianteId,
                    pais_id: paisId
                })
        })

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`)
        }

        const data = await response.json()
        console.log("Respuesta del servidor:", data)
        return data
    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function fetchIncentivoToggle(estudianteId) {
    try {
        const response = await fetch("/incentivo_toggle", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ estudiante_id: estudianteId })
        })

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`)
        }

        const data = await response.json()
        console.log("Respuesta del servidor:", data)
        return data

    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}