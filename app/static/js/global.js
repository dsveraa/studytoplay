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

document.addEventListener("DOMContentLoaded", () => {
    const flash = document.getElementById("flash-messages")
    if (flash) {
        flash.classList.add("show")
    }   
})

document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
      setTimeout(() => alert.remove(), 5000);
    });
  });