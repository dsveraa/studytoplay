class Timer {
  constructor(ms, sec, min, hr) {
    this.ms = ms
    this.sec = sec
    this.min = min
    this.hr = hr
    this.timerSTP = null
  }

  start() {
    this.timerSTP = setInterval(() => {
      this.ms -= 1000

      if (this.ms < 0) {
        this.ms += 1000
        this.sec--
      }

      if (this.sec < 0) {
        this.sec += 60
        this.min--
      }

      if (this.min < 0) {
        this.min += 60
        this.hr--
      }

      UI.updateTimerDisplay(this)
      this.timeIsOver()
    }, 1000)
  }

  stop() {
    clearInterval(this.timerSTP)
  }

  getRemainingTime() { // devuelve ms
    let timeElapsedInMs =
      this.hr * 3600000 +
      this.min * 60000 +
      this.sec * 1000 +
      this.ms
    return Math.floor(timeElapsedInMs / 100) * 100
  }

  setFromServer(data) {
    this.ms = data.ms
    this.sec = data.sec
    this.min = data.min
    this.hr = data.hr
  }

  timeIsOver() {
    if (this.hr === 0 && this.min === 0 && this.sec === 0) {
      clearInterval(this.timerSTP)
      date_fin = getDate()
      sendData(date_inicio, date_fin, 0)
      alert("¡Tiempo terminado!")
    }
  }
}
class UI {
  static updateTimerDisplay(timer_obj) {
    document.querySelector('.second').innerText = String(timer_obj.sec).padStart(2, "0")
    document.querySelector('.minute').innerText = String(timer_obj.min).padStart(2, "0")
    document.querySelector('.hour').innerText = String(timer_obj.hr).padStart(2, "0")
  }

  static disableButton(button) {
    button.disabled = true
  }

  static enableButton(button) {
    button.disabled = false
  }
}

let time = document.querySelector('.tiempo').textContent.trim()
const brokenDownTime = breakDownTime(time)

UI.updateTimerDisplay(brokenDownTime)

function breakDownTime(time) {
  const totalMs = parseInt(time, 10) || 0
  const hours = Math.floor(totalMs / 3600000)
  const remainingMs = totalMs % 3600000
  const minutes = Math.floor(remainingMs / 60000)
  const remainingMsAfterMinutes = remainingMs % 60000
  const seconds = Math.floor(remainingMsAfterMinutes / 1000)
  const milliseconds = remainingMsAfterMinutes % 1000 // Corregido

  return { 'hr': hours, 'min': minutes, 'sec': seconds, 'ms': milliseconds }
}

const timer = new Timer(brokenDownTime.ms, brokenDownTime.sec, brokenDownTime.min, brokenDownTime.hr)
const hourSpan = document.querySelector(".hour")
const minuteSpan = document.querySelector(".minute")
const secondSpan = document.querySelector(".second")
const startBtn = document.querySelector("#start")
const stopBtn = document.querySelector("#stop")

function getDate() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const day = String(now.getDate()).padStart(2, "0")
  const hours = String(now.getHours()).padStart(2, "0")
  const minutes = String(now.getMinutes()).padStart(2, "0")
  const seconds = String(now.getSeconds()).padStart(2, "0")

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}` // "YYYY-MM-DD HH:MM:SS"
}

startBtn.addEventListener("click", async () => {
  try {
    const response = await fetch("/countdown_begins")
    const data = await response.json()
    console.log(data.message)
  } catch (error) {
    console.error("Error al iniciar la cuenta regresiva:", error)
  }

  timer.start()
  timerInspector()
  date_inicio = getDate()
  UI.enableButton(stopBtn)
  UI.disableButton(startBtn)
})

stopBtn.addEventListener("click", () => {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "Esto detendrá el cronómetro.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, detener",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      timer.stop()
      Swal.fire("Detenido", "El cronómetro ha sido detenido.", "success")
      date_fin = getDate()
      sendData(date_inicio, date_fin, timer.getRemainingTime())
    }
  })
})

function sendData(date_inicio, date_fin, remainingTimeMs) {
  fetch("/use_time", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start: date_inicio,
      end: date_fin,
      time: remainingTimeMs,
    }),
  })
    .then((response) => response.json())
    .then(data => {
      if (data.redirect) {
        window.location.href = data.redirect
      }
    })
    .catch((error) => console.error("Error al guardar los datos:", error))
}

function updateTimeToServer() {
  fetch('/update_time', {
    method: 'POST',
    body: JSON.stringify({ time: timer.getRemainingTime() }),
    headers: { 'Content-Type': 'application/json' }
  }).then(response => {
    if (!response.ok) {
      console.error('Error al enviar el tiempo')
    }
  })
}

function timerInspector() {
  timerInterval = setInterval(() => {
    updateTimeToServer()
  }, 5000)
}

async function getServerTime() {
  try {
    const response = await fetch('/get_countdown_time')
    const data = await response.json()
    timer.setFromServer(data)
  } catch (error) {
    console.error("Error al obtener el tiempo del servidor:", error)
  }
}

let lastRequestTime = 0
const minInactiveTime = 5000

document.addEventListener("visibilitychange", () => {
  if (!document.hidden && Date.now() - lastRequestTime > minInactiveTime) {
    console.log("Volviendo a la página, solicitando datos...")
    getServerTime()
  }
})

window.addEventListener("focus", () => {
  if (Date.now() - lastRequestTime > minInactiveTime) {
    console.log("Ventana activa, solicitando datos...")
    getServerTime()
  }
})