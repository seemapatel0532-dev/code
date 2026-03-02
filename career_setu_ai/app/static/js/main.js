window.CareerSetu = {
  toast: (message, category="info") => {
    const toastEl = document.getElementById("csToast");
    const bodyEl = document.getElementById("csToastBody");
    bodyEl.textContent = message;

    toastEl.classList.remove("text-bg-primary","text-bg-success","text-bg-danger","text-bg-warning","text-bg-info");

    const map = {
      success: "text-bg-success",
      danger: "text-bg-danger",
      warning: "text-bg-warning",
      info: "text-bg-info"
    };

    toastEl.classList.add(map[category] || "text-bg-primary");
    new bootstrap.Toast(toastEl, { delay: 2600 }).show();
  },

  showLoader: () => {
    const el = document.getElementById("csLoader");
    if (el) el.classList.remove("d-none");
  },

  hideLoader: () => {
    const el = document.getElementById("csLoader");
    if (el) el.classList.add("d-none");
  },

  // ✅ convenience wrapper for new modules
  loader: (on) => {
    if (on) window.CareerSetu.showLoader();
    else window.CareerSetu.hideLoader();
  },

  resetUploadUI: () => {
    const fileInput = document.getElementById("fileInput");
    const fileName = document.getElementById("fileName");
    const fileMeta = document.getElementById("fileMeta");
    const bar = document.getElementById("uploadBar");
    if (fileInput) fileInput.value = "";
    if (fileName) fileName.textContent = "No file selected";
    if (fileMeta) fileMeta.textContent = "";
    if (bar) bar.style.width = "0%";
  }
};

// Bootstrap form validation
(() => {
  const forms = document.querySelectorAll(".needs-validation");
  Array.from(forms).forEach(form => {
    form.addEventListener("submit", event => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    }, false);
  });
})();

// Upload page interactions: drag-drop + fake progress + loader
(() => {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const chooseBtn = document.getElementById("chooseBtn");
  const uploadForm = document.getElementById("uploadForm");
  const bar = document.getElementById("uploadBar");
  const fileName = document.getElementById("fileName");
  const fileMeta = document.getElementById("fileMeta");

  if (!dropZone || !fileInput || !uploadForm) return;

  const setFileInfo = (file) => {
    if (!file) return;
    if (fileName) fileName.textContent = file.name;
    if (fileMeta) fileMeta.textContent = `${Math.round(file.size/1024)} KB`;
  };

  const fakeProgress = () => {
    if (!bar) return;
    let p = 0;
    bar.style.width = "0%";
    const t = setInterval(() => {
      p += Math.random() * 18;
      if (p >= 90) {
        bar.style.width = "90%";
        clearInterval(t);
      } else {
        bar.style.width = `${p}%`;
      }
    }, 120);
  };

  dropZone.addEventListener("click", () => fileInput.click());
  if (chooseBtn) chooseBtn.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    const f = fileInput.files && fileInput.files[0];
    setFileInfo(f);
  });

  ["dragenter","dragover"].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add("dragover");
    });
  });

  ["dragleave","drop"].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("dragover");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      fileInput.files = files;
      setFileInfo(files[0]);
    }
  });

  uploadForm.addEventListener("submit", () => {
    const f = fileInput.files && fileInput.files[0];
    if (!f) return;
    CareerSetu.showLoader();
    fakeProgress();
  });
})();