const secEl = document.getElementById("second")
const minEl = document.getElementById("minute")
const hrEl = document.getElementById("hour")

let ms = 0, sec = 0, min = 0, hr = 0
let intervalId

const startBtn = document.getElementById("start")
const submitBtn = document.getElementById("stop")

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
  // console.log(date_inicio)

  startBtn.disabled = true

  startBtn.classList.add("active")
  submitBtn.classList.remove("stopActive")
})

submitBtn.addEventListener("click", () => {
  const summary = document.querySelector("#summary").value
  const subject = document.getElementById('asignaturas').value
  
  if (!summary || !subject) {
    alert('Subject and Summary are mandatory')
  } else {
    date_fin = getDate()
    clearInterval(intervalId)
    
    startBtn.classList.remove("active")
    submitBtn.classList.remove("stopActive")
    
    
    let timeElapsedInMs =
      parseInt(hr) * 3600000 +
      parseInt(min) * 60000 +
      parseInt(sec) * 1000 +
      parseInt(ms)
  
    let time = Math.floor(timeElapsedInMs / 100) * 100
  
    sendData(date_inicio, date_fin, summary, time, subject)
  }
})

function putValue() {
  secEl.innerHTML = sec.toString().padStart(2, "0")
  minEl.innerHTML = min.toString().padStart(2, "0")
  hrEl.innerHTML = hr.toString().padStart(2, "0")
}

function sendData(date_inicio, date_fin, summary, time, subject_id) {
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
      subject_id: subject_id
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
      ms = data.ms
      sec = data.sec
      min = data.min
      hr = data.hr
      lastRequestTime = Date.now()
      putValue()
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
  }
})

window.addEventListener("beforeunload", function (event) {
  navigator.sendBeacon("/cancel")
})