class Timer {
  constructor() {
    this.ms = 0
    this.sec = 0
    this.min = 0
    this.hr = 0
    this.timerSTP = null
  }

  start() {
    this.timerSTP = setInterval(() => {
      this.ms++
      if (this.ms === 100) {
        this.ms = 0
        this.sec++
      }
      if (this.sec === 60) {
        this.sec = 0
        this.min++
      }
      if (this.min === 60) {
        this.min = 0
        this.hr++
      }
      UI.updateTimerDisplay(this)
    }, 10)
  }

  stop() {
    clearInterval(this.timerSTP)
  }

  getElapsedTime() {
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
    UI.updateTimerDisplay(this)
  }
}

class UI {
  static updateTimerDisplay(timer) {
    document.getElementById("second").innerText = String(timer.sec).padStart(2, "0")
    document.getElementById("minute").innerText = String(timer.min).padStart(2, "0")
    document.getElementById("hour").innerText = String(timer.hr).padStart(2, "0")
  }

  static disableButton(button) {
    button.disabled = true
  }

  static enableButton(button) {
    button.disabled = false
  }

  static alert(message) {
    alert(message)
  }
}

const timer = new Timer()
const startBtn = document.getElementById("start")
const submitBtn = document.getElementById("stop")
const summaryInput = document.querySelector("#summary")
const subjectInput = document.getElementById('asignaturas')

let date_inicio
let date_fin

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

function validateInputs() {
  return !summaryInput.value || !subjectInput.value
}

async function sendData(date_inicio, date_fin, summary, time, subject_id) {
  try {
    const response = await fetch("/add_time", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start: date_inicio, end: date_fin, summary, time, subject_id })
    })
    const data = await response.json()
    if (data.redirect) {
      window.location.href = data.redirect
    }
  } catch (error) {
    console.error("Error al guardar los datos:", error)
  }
}

startBtn.addEventListener("click", async () => {
  try {
    const response = await fetch("/start_clock")
    const data = await response.json()
    console.log(data.message)
  } catch (error) {
    console.error("Error al iniciar el reloj:", error)
  }

  timer.start()
  date_inicio = getDate()
  console.log(date_inicio)
  UI.disableButton(startBtn)
})

submitBtn.addEventListener("click", () => {
  if (validateInputs()) {
    UI.alert('Subject and Summary are mandatory')
  } else {
    timer.stop()
    date_fin = getDate()

    // console.log(timer.getElapsedTime())
    setTimeout(() => {
      sendData(date_inicio, date_fin, summaryInput.value, timer.getElapsedTime(), subjectInput.value)
    }, 1000)
  }
})

async function getServerTime() {
  try {
    const response = await fetch('/get_time')
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

window.addEventListener("beforeunload", () => {
  navigator.sendBeacon("/cancel")
})
