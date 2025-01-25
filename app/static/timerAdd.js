const secEl = document.getElementById("second")
const minEl = document.getElementById("minute")
const hrEl = document.getElementById("hour")
const startBtn = document.getElementById("start")
const submitBtn = document.getElementById("stop")
let summary = document.querySelector("#summary")
let subject = document.getElementById('asignaturas')

let timer = { ms: 0, sec: 0, min: 0, hr: 0 }
let intervalId

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
    timer.ms++
    if (timer.ms == 100) {
      timer.ms = 0
      timer.sec++
    }
    if (timer.sec == 60) {
      timer.sec = 0
      timer.min++
    }
    if (timer.min == 60) {
      timer.min = 0
      timer.hr++
    }

    putValue()
  }, 10)
}

function stopTime() {
  clearInterval(intervalId)
}

function validateInputs() { 
  return !summary.value || !subject.value
}

function calculateElapsedTime() {
  
  let timeElapsedInMs =
  parseInt(timer.hr) * 3600000 +
  parseInt(timer.min) * 60000 +
  parseInt(timer.sec) * 1000 +
  parseInt(timer.ms)

  return Math.floor(timeElapsedInMs / 100) * 100
}

function putValue() {
  secEl.innerHTML = timer.sec.toString().padStart(2, "0")
  minEl.innerHTML = timer.min.toString().padStart(2, "0")
  hrEl.innerHTML = timer.hr.toString().padStart(2, "0")
}

startBtn.addEventListener("click", () => {
  fetch("/start_clock") // Llamar al backend para iniciar el contador
    .then(response => response.json())
    .then(data => console.log(data.message))
    .catch(error => console.error("Error al iniciar el reloj:", error))

  startTime()
  date_inicio = getDate()
  startBtn.disabled = true
})

submitBtn.addEventListener("click", () => {
  if (validateInputs()) {
    alert('Subject and Summary are mandatory')
  } else {
    stopTime() 

    date_fin = getDate()
    summary = summary.value
    subject = subject.value
    time = calculateElapsedTime()

    console.log(time)
    setTimeout(()=> { 
      sendData(date_inicio, date_fin, summary, time, subject)
    }, 1000)  
  }  
})  

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
      timer.ms = data.ms
      timer.sec = data.sec
      timer.min = data.min
      timer.hr = data.hr
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