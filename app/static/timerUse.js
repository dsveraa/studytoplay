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

  getRemainingTime() {
    let timeElapsedInMs =
      this.hr * 3600000 +
      this.min * 60000 +
      this.sec * 1000 +
      this.ms

    const elapsedTimeMs = Math.floor(timeElapsedInMs / 100) * 100

    return elapsedTimeMs
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

class Hour {
  constructor() {
    this.initialTime = null
    this.initialDate = null
    this.currentDate = null
  }

  getInitialTime() {
    this.initialTime = initialTime
    console.log(`tiempo inicial: ${this.initialTime}`) 
  }

  async getInitialDate() {
    this.initialDate = await this.fetchTime()
    console.log(`fecha inicial: ${this.initialDate}`)
  }

  async getCurrentDate() {
    this.currentDate = await this.fetchTime()
    console.log(`fecha actual: ${this.currentDate}`)

    if (this.initialDate) {
      const differenceMs = this.calculateDifference()
      const currentTime = this.initialTime - differenceMs
      return this.formatDifference(currentTime)

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
    if (!this.initialDate || !this.currentDate) {
      console.error("No se puede calcular la diferencia sin ambas horas")
      return null
    }
    console.log(`tipo de dato currentTime: ${typeof (this.currentDate)}`)
    const difference = this.currentDate - this.initialDate
    console.log(`diferencia entre dates: ${difference}`)
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

const initialTime = document.querySelector('.tiempo').textContent.trim() // ms: str
console.log(initialTime, typeof (initialTime))
const startBtn = document.querySelector("#start")
const stopBtn = document.querySelector("#stop")
const brokenDownTime = breakDownTime(initialTime)

/**
 * Descompone el tiempo desde milisegundos a hora, minuto, segundo.
*
* @param {string} time 
* @returns {{ hr: number; min: number; sec: number; ms: number; }} 
*/
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

const timer = new Timer(
  brokenDownTime.ms,
  brokenDownTime.sec,
  brokenDownTime.min,
  brokenDownTime.hr)

class UI {
  static updateTimerDisplay() {
    document.querySelector('.second').innerText = String(timer.sec).padStart(2, "0")
    document.querySelector('.minute').innerText = String(timer.min).padStart(2, "0")
    document.querySelector('.hour').innerText = String(timer.hr).padStart(2, "0")
  }

  static disableButton(button) {
    button.disabled = true
  }

  static enableButton(button) {
    button.disabled = false
  }
}

UI.updateTimerDisplay(brokenDownTime)

/**
 * Obtiene fecha y hora actual en formato YYYY-MM-DD HH:MM:SS
 *
 * @returns {string} 
 */
function getDate() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const day = String(now.getDate()).padStart(2, "0")
  const hours = String(now.getHours()).padStart(2, "0")
  const minutes = String(now.getMinutes()).padStart(2, "0")
  const seconds = String(now.getSeconds()).padStart(2, "0")

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

startBtn.addEventListener("click", () => {

  timer.start()
  timerInspector()
  date_inicio = getDate()
  UI.enableButton(stopBtn)
  UI.disableButton(startBtn)

  hour.getInitialTime()
  hour.getInitialDate()

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
      console.log("enviando datos al backend")
    }
  })
})

/**
 * Envía momentos de inicio y fin del conteo, como tiempo restante al backend.
 *
 * @param {string} date_inicio 
 * @param {string} date_fin 
 * @param {number} remainingTimeMs 
 */
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
  }, 300000)
}

window.addEventListener("focus", async () => {

  console.log("Ventana activa, solicitando datos...")

  const timeUpdate = await hour.getCurrentDate()

  if (timeUpdate) {
    timer.setFromServer(timeUpdate)
  }
})