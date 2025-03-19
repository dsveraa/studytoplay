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