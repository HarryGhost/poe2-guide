/* R22 checklist enhancement. Content and navigation remain readable without JS. */
(() => {
  'use strict';
  const key = 'poe2-r22-atlas-checks';
  let values = {}, persisted = true;
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || '{}');
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) values = parsed;
  } catch (_) { persisted = false; }
  const groups = [...document.querySelectorAll('[data-eg-group]')];
  const update = group => {
    const inputs = [...group.querySelectorAll('[data-eg-check]')];
    const count = inputs.filter(x => x.checked).length;
    const status = group.nextElementSibling?.querySelector('.eg-check-status');
    if (status) status.textContent = `${count} / ${inputs.length} 已记录 · ${persisted ? '仅保存在当前浏览器，不改变游戏' : '浏览器未允许保存，本次页面有效'}`;
  };
  const save = () => { try { localStorage.setItem(key, JSON.stringify(values)); persisted = true; } catch (_) { persisted = false; } };
  groups.forEach(group => {
    group.querySelectorAll('[data-eg-check]').forEach(input => {
      input.checked = values[input.dataset.egCheck] === true;
      input.addEventListener('change', () => { values[input.dataset.egCheck] = input.checked; save(); update(group); });
    });
    update(group);
  });
  document.querySelectorAll('[data-eg-reset]').forEach(button => {
    button.addEventListener('click', () => {
      const group = groups.find(x => x.dataset.egGroup === button.dataset.egReset);
      if (!group) return;
      group.querySelectorAll('[data-eg-check]').forEach(input => { input.checked = false; delete values[input.dataset.egCheck]; });
      save(); update(group);
    });
  });
})();
