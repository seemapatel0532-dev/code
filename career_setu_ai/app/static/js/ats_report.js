(function () {
  const $ = (id) => document.getElementById(id);

  const scoreChipClass = (score) => {
    if (score >= 85) return "badge bg-success-subtle text-success";
    if (score >= 70) return "badge bg-primary-subtle text-primary";
    if (score >= 55) return "badge bg-warning-subtle text-warning";
    return "badge bg-danger-subtle text-danger";
  };

  const severityBadge = (sev) => {
    const map = {
      high: "badge cs-sev cs-sev-high",
      medium: "badge cs-sev cs-sev-medium",
      low: "badge cs-sev cs-sev-low",
    };
    return map[sev] || "badge text-bg-secondary";
  };

  const setCircle = (score) => {
    const circle = $("atsCircle");
    const fg = circle.querySelector(".ats-fg");
    const r = 46;
    const circumference = 2 * Math.PI * r;
    fg.style.strokeDasharray = `${circumference}`;
    const pct = Math.max(0, Math.min(100, score)) / 100;
    fg.style.strokeDashoffset = `${circumference * (1 - pct)}`;
  };

  const animateNumber = (el, from, to, ms = 900) => {
    const start = performance.now();
    const step = (t) => {
      const p = Math.min(1, (t - start) / ms);
      const v = Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3)));
      el.textContent = v;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const renderBreakdown = (breakdown) => {
    const wrap = $("breakdownWrap");
    wrap.innerHTML = "";
    const entries = Object.values(breakdown || {});
    entries.forEach((item, idx) => {
      const card = document.createElement("div");
      card.className = "ats-break-card";
      card.innerHTML = `
        <button class="ats-break-head" type="button" data-bs-toggle="collapse" data-bs-target="#br_${idx}">
          <div class="d-flex align-items-center justify-content-between w-100">
            <div class="d-flex align-items-center gap-2">
              <span class="${scoreChipClass(item.score)}">${item.score}/100</span>
              <div class="fw-semibold">${item.label}</div>
            </div>
            <i class="bi bi-chevron-down text-muted"></i>
          </div>
          <div class="mt-2">
            <div class="progress" style="height:10px;">
              <div class="progress-bar" role="progressbar" style="width:${item.score}%;"></div>
            </div>
          </div>
        </button>
        <div class="collapse ${idx === 0 ? "show" : ""}" id="br_${idx}">
          <div class="ats-break-body text-muted small">${item.explanation}</div>
        </div>
      `;
      wrap.appendChild(card);
    });
  };

  const renderTips = (tips) => {
    const wrap = $("tipsWrap");
    $("tipsCount").textContent = `${(tips || []).length} tips`;
    wrap.innerHTML = "";

    if (!tips || !tips.length) {
      wrap.innerHTML = `<div class="alert alert-success mb-0">
        <i class="bi bi-check-circle me-1"></i> No major ATS issues found.
      </div>`;
      return;
    }

    const acc = document.createElement("div");
    acc.className = "accordion";
    acc.id = "tipsAcc";

    tips.forEach((t, idx) => {
      const item = document.createElement("div");
      item.className = "accordion-item";
      item.innerHTML = `
        <h2 class="accordion-header">
          <button class="accordion-button ${idx === 0 ? "" : "collapsed"}" type="button"
              data-bs-toggle="collapse" data-bs-target="#tip_${idx}">
            <span class="${severityBadge(t.severity)} me-2">${(t.severity || "low").toUpperCase()}</span>
            ${t.title}
          </button>
        </h2>
        <div id="tip_${idx}" class="accordion-collapse collapse ${idx === 0 ? "show" : ""}" data-bs-parent="#tipsAcc">
          <div class="accordion-body">
            <div class="small text-muted mb-2">${t.explanation}</div>
            <div class="fw-semibold">Fix</div>
            <div class="text-muted small mb-3">${t.fix}</div>

            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="fw-semibold">Copy-ready suggestion</div>
              <button class="btn btn-sm btn-cs-outline" data-copy="${idx}">
                <i class="bi bi-clipboard me-1"></i> Copy
              </button>
            </div>

            <pre class="cs-pre mb-0" id="copyText_${idx}"></pre>
          </div>
        </div>
      `;
      acc.appendChild(item);

      setTimeout(() => {
        const pre = document.getElementById(`copyText_${idx}`);
        if (pre) pre.textContent = t.copy_text || "";
      }, 0);
    });

    wrap.appendChild(acc);

    wrap.querySelectorAll("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const idx = btn.getAttribute("data-copy");
        const pre = document.getElementById(`copyText_${idx}`);
        const txt = pre ? pre.textContent : "";
        if (!txt) return;
        try {
          await navigator.clipboard.writeText(txt);
          window.CareerSetu?.toast("Copied ✅", "success");
        } catch {
          window.CareerSetu?.toast("Copy failed (browser blocked clipboard).", "warning");
        }
      });
    });
  };

  const compute = async (jobDescription = "") => {
    const apiUrl = window.CS_ATS?.apiUrl;
    if (!apiUrl) return;

    try {
      window.CareerSetu?.loader(true);

      const res = await fetch(apiUrl, {
        method: jobDescription ? "POST" : "GET",
        headers: { "Content-Type": "application/json" },
        body: jobDescription ? JSON.stringify({ job_description: jobDescription }) : null,
      });

      const data = await res.json();

      const score = data.ats_score ?? 0;
      const scoreEl = $("atsScoreText");

      setCircle(score);
      animateNumber(scoreEl, parseInt(scoreEl.textContent || "0", 10) || 0, score, 850);

      const badge = $("gradeBadge");
      badge.textContent = data.grade || "—";
      badge.className = `badge ${scoreChipClass(score)}`;

      const metaLine = $("metaLine");
      if (metaLine && data.meta) {
        const usedJD = data.meta.used_job_description ? "Job description: ON" : "Job description: OFF";
        metaLine.textContent = `${usedJD} • Text length: ${data.meta.text_length || 0}`;
      }

      renderBreakdown(data.breakdown || {});
      renderTips(data.improvement_tips || []);

      $("btnCopyTopTips").onclick = async () => {
        const tips = data.improvement_tips || [];
        const blob = tips.map((t, i) => {
          return `#${i + 1} [${(t.severity || "low").toUpperCase()}] ${t.title}\nFix: ${t.fix}\nSuggestion:\n${t.copy_text || ""}\n`;
        }).join("\n");
        try {
          await navigator.clipboard.writeText(blob.trim());
          window.CareerSetu?.toast("Top tips copied ✅", "success");
        } catch {
          window.CareerSetu?.toast("Copy failed (browser blocked clipboard).", "warning");
        }
      };

    } catch (e) {
      console.error(e);
      window.CareerSetu?.toast("Failed to load ATS report.", "danger");
    } finally {
      window.CareerSetu?.loader(false);
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    $("btnRecompute").addEventListener("click", () => {
      compute(($("jobDesc").value || "").trim());
    });
    compute("");
  });
})();