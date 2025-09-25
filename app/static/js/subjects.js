const addSubjectBtn = document.getElementById('add-subject-btn')
const subjectInput = document.getElementById('add-subject')

addSubjectBtn.addEventListener('click', () => {
    const name = subjectInput.value
    addSubject(name)
})

subjectInput.addEventListener('input', () => {
    addSubjectBtn.disabled = subjectInput.value.trim() === ''
})


async function addSubject(name) {
    try {
        const response = await fetch('/subject', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                {
                    subject: name
                })
        })
    
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`)
        }
    
        const data = await response.json()
        window.location.href = '/subject'
        return data

    
    } catch (error) {
        console.error(`Query data error: ${error}`)
        return null
    }
}

async function removeSubject(id) {
    try {
        await fetch('/subject', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                {
                    subject_id: id
                })
        })
    } catch (error) {
        console.error(`Query data error: ${error}`)
        return null
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const closeSubjectBtns = document.querySelectorAll(".close-btn");

    closeSubjectBtns.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.classList.remove('opacity-25')
            btn.classList.add('text-color-orange')
        })
    })

    closeSubjectBtns.forEach(btn => {
        btn.addEventListener('mouseleave', () => {
            btn.classList.add('opacity-25')
            btn.classList.remove('text-color-orange')
        })
    })

    closeSubjectBtns.forEach(btn => {
        btn.addEventListener('click', (event) => {
            const parent = event.target.parentElement
            parent.remove()
            const subjectId = parent.id
            removeSubject(subjectId)      
        })
    })
})

const back = document.getElementById('back-icon')

back.addEventListener('click', () => {
    window.location = '/add_time'
})

