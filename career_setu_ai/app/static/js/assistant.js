// Phase 8 — Optimizer interactivity

function $(id){ return document.getElementById(id); }

function cardSuggestion(text, idx){
  const div = document.createElement('div');
  div.className = 'card border-0 shadow-sm mb-2 cs-hover';
  div.style.cursor = 'pointer';
  div.innerHTML = `
    <div class="card-body">
      <div class="d-flex align-items-center justify-content-between">
        <div class="fw-semibold">Suggestion ${idx+1}</div>
        <span class="badge text-bg-light border">Click to apply</span>
      </div>
      <div class="mt-2">${escapeHtml(text)}</div>
    </div>
  `;
  div.addEventListener('click', () => {
    $('afterText').value = text;
    $('afterBox').textContent = text;
  });
  return div;
}

function escapeHtml(str){
  return (str || '').replace(/[&<>"]+/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m] || m));
}

async function postJSON(url, data){
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data || {})
  });
  const j = await res.json().catch(() => ({}));
  if(!res.ok){
    throw new Error(j.message || 'Request failed');
  }
  return j;
}

function setApplyMsg(html, kind){
  const el = $('applyMsg');
  if(!el) return;
  const cls = kind === 'ok' ? 'alert alert-success' : 'alert alert-danger';
  el.innerHTML = `<div class="${cls} mb-0">${html}</div>`;
}

function renderATS(out){
  const el = $('atsOut');
  if(!el) return;
  const missing = (out.missing_keywords || []).slice(0, 12);
  const tips = out.tips || [];

  let html = '';
  if(missing.length){
    html += `<div class="mb-2"><div class="fw-semibold">Missing Keywords</div>`;
    html += `<div class="d-flex flex-wrap gap-2 mt-2">`;
    missing.forEach(k => html += `<span class="badge rounded-pill text-bg-light border">${escapeHtml(k)}</span>`);
    html += `</div></div>`;
  }
  tips.forEach(t => {
    html += `
      <div class="border rounded p-2 mb-2">
        <div class="fw-semibold">${escapeHtml(t.title || '')}</div>
        <div class="small text-muted mt-1">${escapeHtml(t.detail || '')}</div>
      </div>
    `;
  });
  el.innerHTML = html || `<div class="text-muted">Paste JD and click Analyze.</div>`;
}

function renderRoadmap(out){
  const el = $('roadmapOut');
  if(!el) return;
  const gaps = out.gap_skills || [];
  const roadmap = out.roadmap || [];

  let html = '';
  if(gaps.length){
    html += `<div class="mb-3"><div class="fw-semibold">Gap skills</div>`;
    html += `<div class="d-flex flex-wrap gap-2 mt-2">`;
    gaps.forEach(k => html += `<span class="badge rounded-pill text-bg-light border">${escapeHtml(k)}</span>`);
    html += `</div></div>`;
  }

  if(roadmap.length){
    html += `<div class="accordion" id="roadAcc">`;
    roadmap.forEach((r, idx) => {
      const pid = `road_${idx+1}`;
      html += `
        <div class="accordion-item">
          <h2 class="accordion-header" id="h_${pid}">
            <button class="accordion-button ${idx===0?'':'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#c_${pid}">
              Week ${r.week}: ${escapeHtml(r.skill)}
            </button>
          </h2>
          <div id="c_${pid}" class="accordion-collapse collapse ${idx===0?'show':''}" data-bs-parent="#roadAcc">
            <div class="accordion-body">
              <ul class="mb-0">
                ${(r.plan || []).map(x => `<li>${escapeHtml(x)}</li>`).join('')}
              </ul>
            </div>
          </div>
        </div>
      `;
    });
    html += `</div>`;
  }

  el.innerHTML = html || `<div class="text-muted">Paste JD and click Generate.</div>`;
}


document.addEventListener('DOMContentLoaded', () => {
  const bulletSelect = $('bulletSelect');
  const beforeText = $('beforeText');
  const beforeBox = $('beforeBox');
  const afterBox = $('afterBox');

  function loadSelectedBullet(){
    const opt = bulletSelect?.selectedOptions?.[0];
    const t = opt?.dataset?.text || '';
    beforeText.value = t;
    beforeBox.textContent = t || 'Select a bullet…';
  }

  bulletSelect?.addEventListener('change', loadSelectedBullet);

  $('btnClear')?.addEventListener('click', () => {
    bulletSelect.value = '';
    $('jdText').value = '';
    beforeText.value = '';
    $('afterText').value = '';
    beforeBox.textContent = 'Select a bullet…';
    afterBox.textContent = 'Pick a suggestion…';
    $('suggestions').innerHTML = '';
    setApplyMsg('', 'ok');
    $('atsOut').innerHTML = '';
    $('roadmapOut').innerHTML = '';
  });

  async function doRewrite(){
    const bullet = beforeText.value.trim();
    if(!bullet){
      setApplyMsg('Select a bullet first.', 'bad');
      return;
    }
    const jd_text = $('jdText').value.trim();
    $('suggestions').innerHTML = `<div class="text-muted">Generating suggestions...</div>`;
    try{
      const out = await postJSON('/assistant/api/rewrite', {bullet, jd_text});
      const sug = out.suggestions || [];
      const wrap = document.createElement('div');
      sug.forEach((s, idx) => wrap.appendChild(cardSuggestion(s, idx)));
      $('suggestions').innerHTML = '';
      $('suggestions').appendChild(wrap);
      setApplyMsg('Suggestions generated ✅', 'ok');
    }catch(e){
      $('suggestions').innerHTML = '';
      setApplyMsg(e.message || 'Failed', 'bad');
    }
  }

  $('btnRewrite')?.addEventListener('click', doRewrite);
  $('btnRegenerate')?.addEventListener('click', doRewrite);

  $('btnApply')?.addEventListener('click', async () => {
    const bullet_id = bulletSelect.value;
    const new_text = $('afterText').value.trim();
    if(!bullet_id){
      setApplyMsg('Select a bullet first.', 'bad');
      return;
    }
    if(!new_text){
      setApplyMsg('Pick a suggestion (After is empty).', 'bad');
      return;
    }
    try{
      const out = await postJSON('/assistant/api/apply', {bullet_id, new_text});
      setApplyMsg(out.message || 'Applied ✅', 'ok');

      const opt = bulletSelect.selectedOptions[0];
      if(opt){
        opt.dataset.text = new_text;
      }
      beforeText.value = new_text;
      beforeBox.textContent = new_text;
    }catch(e){
      setApplyMsg(e.message || 'Apply failed', 'bad');
    }
  });

  $('btnSummary')?.addEventListener('click', async () => {
    const jd_text = $('jdText').value.trim();
    $('summaryOut').value = 'Generating...';
    try{
      const out = await postJSON('/assistant/api/summary', {jd_text});
      $('summaryOut').value = out.summary || '';
    }catch(e){
      $('summaryOut').value = '';
      setApplyMsg(e.message || 'Summary failed', 'bad');
    }
  });

  $('btnAts')?.addEventListener('click', async () => {
    const jd_text = $('jdText').value.trim();
    $('atsOut').innerHTML = `<div class="text-muted">Analyzing...</div>`;
    try{
      const out = await postJSON('/assistant/api/ats', {jd_text});
      renderATS(out);
    }catch(e){
      $('atsOut').innerHTML = '';
      setApplyMsg(e.message || 'ATS analyze failed', 'bad');
    }
  });

  $('btnRoadmap')?.addEventListener('click', async () => {
    const jd_text = $('jdText').value.trim();
    $('roadmapOut').innerHTML = `<div class="text-muted">Generating roadmap...</div>`;
    try{
      const out = await postJSON('/assistant/api/roadmap', {jd_text});
      renderRoadmap(out);
    }catch(e){
      $('roadmapOut').innerHTML = '';
      setApplyMsg(e.message || 'Roadmap failed', 'bad');
    }
  });

});