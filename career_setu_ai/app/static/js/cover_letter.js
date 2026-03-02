function $(id){ return document.getElementById(id); }

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

function syncHidden(){
  const company = $('company').value || '';
  const role = $('role').value || '';
  const jd = $('jdText').value || '';
  const letter = $('letter').value || '';

  $('pdf_company').value = company;
  $('pdf_role').value = role;
  $('pdf_jd').value = jd;
  $('pdf_letter').value = letter;

  $('docx_company').value = company;
  $('docx_role').value = role;
  $('docx_jd').value = jd;
  $('docx_letter').value = letter;
}

document.addEventListener('DOMContentLoaded', () => {
  const btnGen = $('btnGen');
  const btnRegen = $('btnRegen');
  const btnCopy = $('btnCopy');

  async function generate(){
    const company = $('company').value.trim();
    const role = $('role').value.trim();
    const jd_text = $('jdText').value.trim();

    $('letter').value = 'Generating...';
    try{
      const out = await postJSON('/assistant/api/cover-letter', {company, role, jd_text});
      $('letter').value = out.letter || '';
      syncHidden();
    }catch(e){
      $('letter').value = '';
      $('copyMsg').innerHTML = `<div class="alert alert-danger mb-0">${e.message}</div>`;
    }
  }

  btnGen?.addEventListener('click', generate);
  btnRegen?.addEventListener('click', generate);

  ['company','role','jdText','letter'].forEach(id => {
    $(id)?.addEventListener('input', syncHidden);
  });

  btnCopy?.addEventListener('click', async () => {
    const text = $('letter').value || '';
    if(!text.trim()) return;
    try{
      await navigator.clipboard.writeText(text);
      $('copyMsg').innerHTML = `<div class="alert alert-success mb-0">Copied ✅</div>`;
      setTimeout(() => $('copyMsg').innerHTML = '', 1200);
    }catch(e){
      $('copyMsg').innerHTML = `<div class="alert alert-warning mb-0">Copy failed. Select text and copy manually.</div>`;
    }
  });
});