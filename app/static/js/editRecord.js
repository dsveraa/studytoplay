function saveChanges() {
    let summary = document.getElementById("summary").value

    fetch(window.location.href, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ summary: summary })
    }).then(response => {
        if (response.redirected) {
            window.location.href = response.url
        }
    })
}

document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.querySelector("textarea")

    textarea.addEventListener("keydown", function (event) {
        if (event.key === "Tab") {
            event.preventDefault()

            const start = this.selectionStart
            const end = this.selectionEnd
            const beforeCursor = this.value.substring(0, start)
            const afterCursor = this.value.substring(end)

            if (event.shiftKey) {
                // Shift + Tab: Eliminar tabulación anterior si existe
                const lineStart = beforeCursor.lastIndexOf("\n") + 1
                const line = this.value.substring(lineStart, start)

                if (line.startsWith("\t")) {
                    // Si hay un tabulador, lo eliminamos
                    this.value = beforeCursor.substring(0, lineStart) + line.substring(1) + afterCursor
                    this.selectionStart = this.selectionEnd = start - 1
                } else if (line.startsWith("    ")) {
                    // Si hay cuatro espacios, eliminamos esos espacios
                    this.value = beforeCursor.substring(0, lineStart) + line.substring(4) + afterCursor
                    this.selectionStart = this.selectionEnd = start - 4
                }
            } else {
                // Tab normal: Insertar tabulación
                this.value = beforeCursor + "\t" + afterCursor
                this.selectionStart = this.selectionEnd = start + 1
            }
        }
    })
})
