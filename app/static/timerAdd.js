
function logClick(boton) {
  const now = new Date().toLocaleString()
  fetch('log_click', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ boton: boton, hora_cliente: now})
  }).then(response => {
    if (response.ok) {
      console.log("Log enviado")
    }
  })
}

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

class Hour {
  constructor() {
    this.initialTime = null
    this.currentTime = null
  }

  async getInitialTime() {
    this.initialTime = await this.fetchTime()
    console.log(this.initialTime)
  }

  async getCurrentTime() {
    this.currentTime = await this.fetchTime()
    console.log(this.currentTime)

    if (this.initialTime) {
      const differenceMs = this.calculateDifference()
      console.log(differenceMs)
      return this.formatDifference(differenceMs)

    }
  }

  async fetchTime() {
    try {
      const response = await fetch('/get_time')
      const data = await response.json()
      const stringToDate = new Date(data.current_time)
      return stringToDate

    } catch (error) {
      console.error('Error al obtener la hora:', error)
      return null
    }
  }

  calculateDifference() {
    if (!this.initialTime || !this.currentTime) {
      console.error("No se puede calcular la diferencia sin ambas horas")
      return null
    }
    console.log(typeof (this.currentTime))
    const difference = this.currentTime - this.initialTime
    console.log(difference)
    return difference
  }

  formatDifference(differenceMs) {
    if (differenceMs === null) return null

    const ms = differenceMs % 1000
    const totalSeconds = Math.floor(differenceMs / 1000)
    const sec = totalSeconds % 60
    const totalMinutes = Math.floor(totalSeconds / 60)
    const min = totalMinutes % 60
    const hr = Math.floor(totalMinutes / 60)

    return { ms, sec, min, hr }
  }

}

const hour = new Hour()
const timer = new Timer()
const startBtn = document.getElementById("start")
const submitBtn = document.getElementById("stop")
const summaryInput = document.querySelector("#summary")
const subjectInput = document.getElementById('asignaturas')
const cancelBtn = document.getElementById('cancel')

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
      window.location.href = data.redirect + "?reload=true"
    }
  } catch (error) {
    console.error("Error al guardar los datos:", error)
  }
}

function switchStudying() {
  fetch('/switch_status/studying', {
    method: 'POST',
    headers: {'X-Requested-With': 'XMLHttpRequest'}
  })
  .then(response => response.json())
  .then(data => {console.log('Nuevo estado:', data)
  })
  .catch(error => {
    console.error('Error', error)
  })
}

startBtn.addEventListener("click", () => {

  timer.start()
  date_inicio = getDate()
  // console.log(date_inicio)
  // console.log(typeof(date_inicio))
  UI.disableButton(startBtn)

  hour.getInitialTime()
  switchStudying()
})

async function switchIdle() {
  try {
    const response = await fetch('/switch_status/idle', {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    const data = await response.json()
    console.log('Nuevo estado:', data)
  } catch (error) {
    console.error('Error', error)
  }
}


submitBtn.addEventListener("click", () => {
  if (validateInputs()) {
    UI.alert('Subject and Summary are mandatory')
  } else {
    timer.stop()
    date_fin = getDate()

    setTimeout(() => {
      sendData(date_inicio, date_fin, summaryInput.value, timer.getElapsedTime(), subjectInput.value)
    }, 1000)
  }

  switchIdle()
})

cancelBtn.addEventListener("click", () => {
  switchIdle().then(() => {
    window.location.href = "/perfil"  
  })
})

window.addEventListener("focus", async () => {

  console.log("Ventana activa, solicitando datos...")

  const timeUpdate = await hour.getCurrentTime()
  console.log(timeUpdate, typeof(timeUpdate))

  if (timeUpdate) {
    timer.setFromServer(timeUpdate)
  }

})

window.addEventListener("beforeunload", () => {
  navigator.sendBeacon("/cancel")
})
