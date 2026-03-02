(function () {
  const search = document.getElementById("jdSearch");
  const grid = document.getElementById("jdGrid");

  // Search/filter cards live (client side)
  const applyFilter = () => {
    if (!grid || !search) return;
    const q = (search.value || "").trim().toLowerCase();

    const cards = grid.querySelectorAll(".jd-card");
    cards.forEach(card => {
      const hay = [
        card.getAttribute("data-title") || "",
        card.getAttribute("data-role") || "",
        card.getAttribute("data-skills") || ""
      ].join(" ");

      const col = card.closest(".jd-card-col");
      if (!q || hay.includes(q)) {
        if (col) col.classList.remove("d-none");
      } else {
        if (col) col.classList.add("d-none");
      }
    });
  };

  if (search) {
    search.addEventListener("input", applyFilter);
    applyFilter();
  }

  // Delete modal wiring
  const deleteModal = document.getElementById("deleteModal");
  if (deleteModal) {
    deleteModal.addEventListener("show.bs.modal", (event) => {
      const btn = event.relatedTarget;
      if (!btn) return;

      const id = btn.getAttribute("data-jd-id");
      const title = btn.getAttribute("data-jd-title");

      const titleEl = document.getElementById("deleteTitle");
      const form = document.getElementById("deleteForm");

      if (titleEl) titleEl.textContent = title || "—";
      if (form && id) form.action = `/jds/${id}/delete`;
    });
  }
})();