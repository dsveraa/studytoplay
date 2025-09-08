async function deleteRestriction(estudiante_id, restriction_id) {
    const response = await fetch(`/restriction/${estudiante_id}/${restriction_id}`, {
        method: "DELETE"
    })

    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`)
    return restriction_id
}

async function deleteIncentive(estudiante_id, incentive_id) {
    const response = await fetch(`/incentive/${estudiante_id}/${incentive_id}`, {
        method: "DELETE"
    })
    
    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`)
    return incentive_id
}

async function addIncentive(estudianteId, monto, nota, simbolo, moneda) {
    try {
        const response = await fetch("/incentive", {
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
        return data
    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function addRestriction(estudianteId, mensaje) {
    try {
        const response = await fetch("/restriction", {
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
        return data
    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function fetchCambiarPais(estudianteId, paisId) {
    try {
        const response = await fetch(`/country/${estudianteId}/${paisId}`, {
            method: "PUT"
        })

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`)
        }

        const data = await response.json()
        return data
    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function fetchIncentivoToggle(estudianteId) {
    try {
        const response = await fetch(`/incentivo/${estudianteId}`, {
            method: "PUT"
        })

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`)
        }

        const data = await response.json()
        return data

    } catch (error) {
        console.error("Error al consultar los datos", error)
        return null
    }
}

async function fetchSetTrophy(estudianteId, reward) {
    try {
        const response = await fetch(`/trophy/${estudianteId}/${encodeURIComponent(reward)}`, {
            method: "PUT"
        })

        const data = await response.json()

        if (data.flash) {
            showFlashMessage(data.flash.message, data.flash.category)
        }

    } catch (error) {
        console.error("Error al consultar los datos", error)
    }
}

async function fetchSetExtraTime(id, extraTime) {
    try {
      const response = await fetch(`/extra_time/${id}/${extraTime}`, {
        method: "PUT"
      })
  
      const data = await response.json()
      return data

    } catch (error) {
      console.error("Error al consultar los datos", error)
    }

  }

async function fetchTimeFunRatio(id, estudianteId) {
    try {
        const response = await fetch(`/study_fun_ratio/${id}/${estudianteId}`, {
            method: "PUT"
        })

        const data = await response.json()
        return data

    } catch (error) {
        console.error("Error al consultar los datos", error)
    }
}
