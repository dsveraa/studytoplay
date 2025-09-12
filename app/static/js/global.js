// con recarga

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".btn-loading").forEach(btn => {
        btn.addEventListener("click", () => {
            if (!btn.classList.contains("loading")) {
                btn.classList.add("loading")
            }
        })
    })
})

// sin recarga

function withLoader(btn, asyncFunc) {
    btn.addEventListener("click", async () => {
        if (btn.classList.contains("loading")) return

        btn.classList.add("loading")
        try {
            await asyncFunc()
        } catch (err) {
            console.error(err)
        } finally {
            btn.classList.remove("loading")
        }
    })
}
