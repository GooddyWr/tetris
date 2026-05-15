/* ═══════════════════════════════════════════
   main.js — логика навигации и кнопок
   ═══════════════════════════════════════════ */

'use strict';

/* ── Переключение вкладок ── */
function showTab(id) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

  document.getElementById(id).classList.add('active');

  // Найти кнопку по onclick-атрибуту
  const btn = document.querySelector(`.tab[onclick="showTab('${id}')"]`);
  if (btn) btn.classList.add('active');
}

/* ── После скачивания — перейти на "how to run" ── */
function switchToHowTo() {
  setTimeout(() => {
    showTab('howto');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, 200);
}

/* ── Копирование кода ── */
function copyCode(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = 'copied ✓';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = orig;
      btn.classList.remove('copied');
    }, 2000);
  }).catch(() => {
    // Фолбэк для старых браузеров
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    btn.textContent = 'copied ✓';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = 'copy';
      btn.classList.remove('copied');
    }, 2000);
  });
}
