// ===== MEASLES SENTINEL — MAIN JS =====

// ===== THEME =====
const savedTheme = localStorage.getItem("ms-theme") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);

export function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("ms-theme", next);
  const btn = document.getElementById("themeBtn");
  if (btn) btn.textContent = next === "dark" ? "☀️" : "🌙";
}

// ===== TOAST =====
export function showToast(message, type = "info", duration = 3500) {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const icons = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || icons.info}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.classList.add("hide"); setTimeout(() => toast.remove(), 300); }, duration);
}

// ===== SPLASH =====
export function hideSplash() {
  const splash = document.getElementById("splash");
  if (splash) {
    setTimeout(() => splash.classList.add("hidden"), 2200);
  }
}

// ===== TABS =====
export function initTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const panel = document.getElementById(target);
      if (panel) panel.classList.add("active");
    });
  });
}

// ===== SYMPTOM CHECKLIST =====
export function initSymptoms() {
  document.querySelectorAll(".symptom-item").forEach(item => {
    item.addEventListener("click", () => {
      item.classList.toggle("checked");
      const cb = item.querySelector(".symptom-checkbox");
      if (cb) cb.innerHTML = item.classList.contains("checked") ? "✓" : "";
      updateSymptomScore();
    });
  });
}

function updateSymptomScore() {
  const checked = document.querySelectorAll(".symptom-item.checked").length;
  const total = document.querySelectorAll(".symptom-item").length;
  const scoreEl = document.getElementById("symptomScore");
  if (scoreEl) {
    const pct = Math.round((checked / total) * 100);
    scoreEl.textContent = `${checked}/${total}`;
    const fill = document.getElementById("symptomScoreFill");
    if (fill) fill.style.width = pct + "%";
    const risk = document.getElementById("symptomRisk");
    if (risk) {
      if (pct >= 60) {
        risk.textContent = "High";
        risk.className = "badge badge-danger";
      } else if (pct >= 30) {
        risk.textContent = "Moderate";
        risk.className = "badge badge-warning";
      } else {
        risk.textContent = "Low";
        risk.className = "badge badge-success";
      }
    }
  }
  const savedSymptoms = [...document.querySelectorAll(".symptom-item.checked")]
    .map(i => i.querySelector(".symptom-name")?.textContent).filter(Boolean);
  sessionStorage.setItem("ms-symptoms", JSON.stringify(savedSymptoms));
}

// ===== UPLOAD =====
export function initUpload() {
  const zone = document.getElementById("uploadZone");
  const input = document.getElementById("fileInput");
  const preview = document.getElementById("imagePreview");
  const previewImg = document.getElementById("previewImg");
  const analyzeBtn = document.getElementById("analyzeBtn");

  if (!zone || !input) return;

  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("drag-over"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", e => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
  input.addEventListener("change", () => { if (input.files[0]) handleFile(input.files[0]); });

  function handleFile(file) {
    if (!file.type.startsWith("image/")) { showToast("Please upload an image file.", "error"); return; }
    if (file.size > 10 * 1024 * 1024) { showToast("File too large. Max 10MB.", "error"); return; }
    const url = URL.createObjectURL(file);
    if (previewImg) previewImg.src = url;
    if (preview) preview.style.display = "block";
    if (zone) zone.style.display = "none";
    sessionStorage.setItem("ms-imageFile", url);
    sessionStorage.setItem("ms-imageName", file.name);
    if (analyzeBtn) analyzeBtn.disabled = false;
    showToast("Image loaded. Ready to analyze.", "success");
  }
}

// ===== CONFIDENCE BAR ANIMATION =====
export function animateBar(id, value) {
  const fill = document.getElementById(id);
  if (!fill) return;
  fill.style.width = "0%";
  requestAnimationFrame(() => {
    setTimeout(() => { fill.style.width = value + "%"; }, 100);
  });
}

// ===== REPORT DOWNLOAD =====
export function downloadReport(reportData) {
  const content = `
MEASLES SENTINEL — SCREENING REPORT
=====================================
AI-assisted screening only. Consult a healthcare professional.
=====================================

Date: ${new Date().toLocaleString()}
Patient: ${reportData.name || "Anonymous"}

RESULT
------
Condition:  ${reportData.condition}
Confidence: ${reportData.confidence}%
Risk Level: ${reportData.risk}

SYMPTOMS REPORTED
-----------------
${(reportData.symptoms || []).join("\n") || "None reported"}

GUIDANCE
--------
${(reportData.guidance || []).map((g, i) => `${i+1}. ${g}`).join("\n")}

DISCLAIMER
----------
This report is generated by an AI screening tool and is NOT a medical
diagnosis. Always consult a qualified healthcare professional.

=====================================
© Measles Sentinel — ${new Date().getFullYear()}
  `;
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `measles-sentinel-report-${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Report downloaded.", "success");
}

// ===== INIT ON DOM =====
document.addEventListener("DOMContentLoaded", () => {
  // Theme button
  const themeBtn = document.getElementById("themeBtn");
  if (themeBtn) {
    themeBtn.textContent = savedTheme === "dark" ? "☀️" : "🌙";
    themeBtn.addEventListener("click", toggleTheme);
  }
  // Splash
  hideSplash();
  // Tabs
  initTabs();
  // Symptoms
  initSymptoms();
  // Upload
  initUpload();
  // Active nav
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(l => {
    if (l.getAttribute("href") === path) l.classList.add("active");
  });
});
