const session_secret = "perri" //vulnerabilidad, solucionar.

function encryptData(data) {
  return CryptoJS.AES.encrypt(JSON.stringify(data), session_secret).toString()
}

function decryptData(encryptedData) {
  const bytes = CryptoJS.AES.decrypt(encryptedData, session_secret)
  return JSON.parse(bytes.toString(CryptoJS.enc.Utf8))
}

const startBtn = document.getElementById('start_button')
const stopBtn = document.getElementById('stop_button')
const counter = document.getElementById('counter')

let sessionTime

const rt_element = document.createElement('p')

let interval

let countdownRunning = null
let currentTime = null
countdownRunning = localStorage.getItem('cd_running')

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

stopBtn.addEventListener("click", () => {
  Swal.fire({
    title: "What activity have you done?",
    input: "text",
    inputPlaceholder: "Videogames, watching Youtube, etc...",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Guardar",
    cancelButtonText: "Cancelar",
    inputValidator: (value) => {
      if (!value) {
        return "You must instert an activity"
      }
    },
  }).then((result) => {
    if (result.isConfirmed) {
      const actividad = result.value 
      
      countdownRunning = false
      stopCountdown()

      let initialTime = localStorage.getItem('initial_time')
      let finalTime = new Date().toISOString()

      const differenceTime = new Date(finalTime) - new Date(initialTime)
      const updatedTime = sessionTime - differenceTime

      
      stopBtn.disabled = true
      
      date_inicio = localStorage.getItem('date_inicio')
      date_fin = getDate()
      
      localStorage.removeItem('initial_time')
      localStorage.removeItem('cd_running')
      localStorage.removeItem('current_time')
      localStorage.removeItem('session_time')
      localStorage.removeItem('date_inicio')

      sendData(date_inicio, date_fin, updatedTime, actividad)
      console.log("Enviando datos al backend:", actividad)
      
    }
  })
  switchIdle()
})

function stopCountdown() {
  clearInterval(interval)
}

function startCountdown() {
  if (countdownRunning) {
    currentTime = localStorage.getItem('current_time')
  } else {
    currentTime = decryptData(localStorage.getItem('session_time'))
  }

  interval = setInterval(()=> {
      currentTime = currentTime -1000
      counter.removeChild(rt_element)
      const HMS = msToHMS(currentTime)
      rt_element.textContent = HMS
      counter.appendChild(rt_element)
      localStorage.setItem('current_time', currentTime)

      if (currentTime <= 0) {
          clearInterval(interval)
      }
  }, 1000)
}

function msToHMS(ms) {
let totalSeconds = Math.floor(ms / 1000)
let hours = Math.floor(totalSeconds / 3600)
let minutes = Math.floor((totalSeconds % 3600) / 60)
let seconds = totalSeconds % 60

return [hours, minutes, seconds]
    .map(unit => String(unit).padStart(2, '0'))
    .join(':')
}

function switchPlaying() {
  fetch('/switch_status/playing', {
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

startBtn.addEventListener('click', ()=> {
  localStorage.setItem('initial_time', new Date().toISOString())
  localStorage.setItem('cd_running', true)
  localStorage.setItem('date_inicio', getDate())

  startCountdown()

  startBtn.disabled = true
  stopBtn.disabled = false

  switchPlaying()
})

async function onLoad() {
  let HMS

  if (countdownRunning) {
    console.log('countdown running')
    currentTime = localStorage.getItem('current_time')
    sessionTime = decryptData(localStorage.getItem('session_time'))

    console.log('currentTime:', currentTime)
    
    stopBtn.disabled = false
    startBtn.disabled = true
    HMS = msToHMS(currentTime)
    
    console.log(HMS)
    
    rt_element.textContent = HMS // <p>HMS</p>
    counter.appendChild(rt_element)
    startCountdown()
    return
  }

  stopBtn.disabled = true
  startBtn.disabled = false
  
  const time = await fetchTime()
  
  encryptedTime = encryptData(time)
  localStorage.setItem("session_time", encryptedTime)
  
  sessionTime = decryptData(localStorage.getItem('session_time'))

  HMS = msToHMS(sessionTime)
  rt_element.textContent = HMS
  counter.appendChild(rt_element)
}

async function fetchTime() {
  try {
      const response = await fetch("/get_remaining_time")
      if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`)
      }
      const data = await response.json()
      return data.remaining_time
  } catch (error) {
      console.error("error al consultar los datos", error)
      return null
  }
}

/**
 * Envía momentos de inicio y fin del conteo, como tiempo restante al backend.
 *
 * @param {string} date_inicio 
 * @param {string} date_fin 
 * @param {number} remainingTimeMs 
 */
function sendData(date_inicio, date_fin, remainingTimeMs, actividad) {
  fetch("/use_time", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start: date_inicio,
      end: date_fin,
      time: remainingTimeMs,
      actividad: actividad,
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


window.addEventListener("focus", () => {
  let initialTime = localStorage.getItem('initial_time')
  console.log('initialTime:', initialTime)
  let finalTime = new Date().toISOString()
  console.log('finalTime:', finalTime)
  let diffTime = new Date(finalTime) - new Date(initialTime)
  console.log('diffTime:', diffTime)
  
  const sessionTimeInt = parseInt(sessionTime)
  console.log('typeof sessionTimeInt:', typeof(sessionTimeInt))
  
  currentTime = (sessionTimeInt - diffTime)
  console.log('typeof diffTime:', typeof(diffTime))
  console.log('currentTime:', currentTime)
})


onLoad()