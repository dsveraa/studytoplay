const secEl = document.getElementById("second")
const minEl = document.getElementById("minute")
const hrEl = document.getElementById("hour")


let ms = 0, sec = 0, min = 0, hr = 0
let intervalId

const startBtn = document.getElementById("start")
const stopBtn = document.getElementById("stop")

const cancelBtn = document.getElementById("cancel")

let date_inicio
let date_fin

function getDate() {
  let currentDate = new Date()

  let year = currentDate.getFullYear()
  let month = (currentDate.getMonth() + 1).toString().padStart(2, "0")
  let day = currentDate.getDate().toString().padStart(2, "0")
  let hours = currentDate.getHours().toString().padStart(2, "0")
  let minutes = currentDate.getMinutes().toString().padStart(2, "0")
  let seconds = currentDate.getSeconds().toString().padStart(2, "0")

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

function startTime() {
  intervalId = setInterval(() => {
    ms++
    if (ms == 100) {
      ms = 0
      sec++
    }
    if (sec == 60) {
      sec = 0
      min++
    }
    if (min == 60) {
      min = 0
      hr++
    }

    putValue()
  }, 10)
}


startBtn.addEventListener("click", () => {
  fetch("/start_clock") // Llamar al backend para iniciar el contador
    .then(response => response.json())
    .then(data => console.log(data.message))
    .catch(error => console.error("Error al iniciar el reloj:", error))

  startTime()
  date_inicio = getDate()
  console.log(date_inicio)

  startBtn.disabled = true

  startBtn.classList.add("active")
  stopBtn.classList.remove("stopActive")
})

stopBtn.addEventListener("click", () => {
  date_fin = getDate()
  clearInterval(intervalId) // Detener el temporizador correctamente

  console.log("Deteniendo el reloj...")
  fetch("/stop_clock", { method: "GET" })

  startBtn.classList.remove("active")
  stopBtn.classList.remove("stopActive")

  const summary = document.querySelector("#summary").value

  let timeElapsedInMs =
    parseInt(hr) * 3600000 +
    parseInt(min) * 60000 +
    parseInt(sec) * 1000 +
    parseInt(ms)

  let time = Math.floor(timeElapsedInMs / 100) * 100

  sendData(date_inicio, date_fin, summary, time)
})


function putValue() {
  secEl.innerHTML = sec.toString().padStart(2, "0")
  minEl.innerHTML = min.toString().padStart(2, "0")
  hrEl.innerHTML = hr.toString().padStart(2, "0")
}

function sendData(date_inicio, date_fin, summary, time) {
  fetch("/save_study", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start: date_inicio,
      end: date_fin,
      summary: summary,
      time: time,
    }),
  })
    .then((response) => response.json())
    .then(data => {
      if (data.redirect) {
        //me redirige al endpoint especificado en el backend (perfil)
        window.location.href = data.redirect
      }
    })
    .catch((error) => console.error("Error al guardar los datos:", error))
}

let lastRequestTime = 0
let minInactiveTime = 5 * 1000

function getServerTime() {
  fetch('/get_time')
    .then(response => response.json())
    .then(data => {
      // Solo actualizar los valores, sin reiniciar el contador
      ms = data.ms
      sec = data.sec
      min = data.min
      hr = data.hr
      lastRequestTime = Date.now()
      putValue() // Actualiza la UI sin afectar la ejecución del temporizador
    })
    .catch(error => console.error(error))
}

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    let now = Date.now()
    if (now - lastRequestTime > minInactiveTime) {
      console.log("Volviendo a la página, solicitando datos...")
      getServerTime()
    }
  }
})

window.addEventListener("focus", () => {
  let now = Date.now()
  if (now - lastRequestTime > minInactiveTime) {
    console.log("Ventana activa, solicitando datos...")
    getServerTime()
    console.log(sec)
  }
})

window.addEventListener("beforeunload", () => {
  console.log("Deteniendo el reloj...")
  fetch("/stop_clock", { method: "GET" })
})

cancelBtn.addEventListener('click', () => {
  fetch("/stop_clock", { method: "GET" })
    .then(response => response.json())
    .then(data => console.log("Respuesta del backend:", data))
    .catch(error => console.error("Error al detener el reloj:", error))
  console.log("Deteniendo el reloj...")
})