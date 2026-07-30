/**
 * MDPDF Web Interface — Dark Minimal
 */

// DOM Elements
const dropzone = document.getElementById("dropzone");
const dropzoneContent = document.getElementById("dropzoneContent");
const dropzoneActive = document.getElementById("dropzoneActive");
const fileInput = document.getElementById("fileInput");
const selectFileBtn = document.getElementById("selectFileBtn");
const fileList = document.getElementById("fileList");
const convertBtn = document.getElementById("convertBtn");
const styleSelect = document.getElementById("styleSelect");
const tocToggle = document.getElementById("tocToggle");
const tocLevel = document.getElementById("tocLevel");
const emptyState = document.getElementById("emptyState");
const progressSection = document.getElementById("progressSection");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const resultsSection = document.getElementById("resultsSection");
const resultsInfo = document.getElementById("resultsInfo");
const resultsList = document.getElementById("resultsList");
const clearResultsBtn = document.getElementById("clearResultsBtn");
const previewSection = document.getElementById("previewSection");
const pdfPreview = document.getElementById("pdfPreview");
const versionBadge = document.getElementById("versionBadge");

// State
let files = [];
let results = [];

// ============================================================
// Utilities
// ============================================================

function formatSize(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

function validExtension(name) {
    const valid = [".md", ".markdown", ".mdown", ".mkd", ".mkdn"];
    const ext = "." + name.split(".").pop().toLowerCase();
    return valid.includes(ext);
}

// ============================================================
// File Management
// ============================================================

function addFiles(newFiles) {
    for (const file of newFiles) {
        if (!validExtension(file.name)) continue;
        if (files.some(f => f.name === file.name && f.size === file.size)) continue;
        files.push(file);
    }
    renderFileList();
    updateConvertBtn();
}

function removeFile(index) {
    files.splice(index, 1);
    renderFileList();
    updateConvertBtn();
}

function renderFileList() {
    fileList.innerHTML = "";
    files.forEach((file, i) => {
        const chip = document.createElement("div");
        chip.className = "file-chip";
        chip.innerHTML = `
            <i data-lucide="file-text" class="file-icon"></i>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatSize(file.size)}</div>
            </div>
            <button class="btn-remove" data-index="${i}" title="Remove">
                <i data-lucide="x"></i>
            </button>
        `;
        fileList.appendChild(chip);
    });
    // Re-init lucide icons for new elements
    lucide.createIcons();
    // Attach remove handlers
    fileList.querySelectorAll(".btn-remove").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            removeFile(parseInt(btn.dataset.index));
        });
    });
}

function updateConvertBtn() {
    convertBtn.disabled = files.length === 0;
}

// ============================================================
// Conversion
// ============================================================

async function convertFiles() {
    results = [];
    showProgress();
    const total = files.length;

    for (let i = 0; i < total; i++) {
        const file = files[i];
        updateProgress(((i) / total) * 100, `Converting ${file.name}...`);

        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("style", styleSelect.value);
            formData.append("toc", tocToggle.checked);
            formData.append("toc_level", tocLevel.value);

            const response = await fetch("/api/convert", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || `Error ${response.status}`);
            }

            const buffer = await response.arrayBuffer();
            const blob = new Blob([buffer], { type: "application/pdf" });
            const url = URL.createObjectURL(blob);
            const pdfName = file.name.replace(/\.(md|markdown|mdown|mkd|mkdn)$/i, ".pdf");

            results.push({ name: pdfName, size: blob.size, url, success: true });
        } catch (err) {
            results.push({ name: file.name, error: err.message, success: false });
        }

        updateProgress(((i + 1) / total) * 100, `${i + 1}/${total} done`);
    }

    showResults();
}

// ============================================================
// UI States
// ============================================================

function hideAllRightPanel() {
    emptyState.hidden = true;
    progressSection.hidden = true;
    resultsSection.hidden = true;
    previewSection.hidden = true;
}

function showEmpty() {
    hideAllRightPanel();
    emptyState.hidden = false;
}

function showProgress() {
    hideAllRightPanel();
    progressSection.hidden = false;
    progressBar.style.width = "0%";
    convertBtn.disabled = true;
}

function updateProgress(percent, text) {
    progressBar.style.width = percent + "%";
    progressText.textContent = text;
}

function showResults() {
    hideAllRightPanel();
    resultsSection.hidden = false;
    convertBtn.disabled = false;

    const successes = results.filter(r => r.success).length;
    const failures = results.length - successes;
    let info = `${successes} file${successes !== 1 ? "s" : ""} converted`;
    if (failures > 0) info += `, ${failures} failed`;
    resultsInfo.textContent = info;

    renderResults();
}

function renderResults() {
    resultsList.innerHTML = "";
    results.forEach((r, i) => {
        const item = document.createElement("div");
        item.className = "result-item";
        if (r.success) {
            item.innerHTML = `
                <i data-lucide="check-circle" style="width:16px;height:16px;color:var(--success)"></i>
                <span class="result-name">${r.name}</span>
                <span class="result-size">${formatSize(r.size)}</span>
                <div class="result-actions">
                    <button class="btn-preview" data-index="${i}" title="Preview">
                        <i data-lucide="eye"></i> Preview
                    </button>
                    <a class="btn-download" href="${r.url}" download="${r.name}">
                        <i data-lucide="download"></i> Download
                    </a>
                    <button class="btn-remove-result" data-index="${i}" title="Remove">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            `;
        } else {
            item.innerHTML = `
                <i data-lucide="alert-triangle" style="width:16px;height:16px;color:var(--error)"></i>
                <span class="result-name">${r.name}</span>
                <span class="result-size" style="color:var(--error)">${r.error}</span>
                <div class="result-actions">
                    <button class="btn-remove-result" data-index="${i}" title="Remove">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            `;
        }
        resultsList.appendChild(item);
    });
    lucide.createIcons();

    // Attach preview handlers
    resultsList.querySelectorAll(".btn-preview").forEach(btn => {
        btn.addEventListener("click", () => openPreview(parseInt(btn.dataset.index)));
    });

    // Attach individual remove handlers
    resultsList.querySelectorAll(".btn-remove-result").forEach(btn => {
        btn.addEventListener("click", () => removeResult(parseInt(btn.dataset.index)));
    });
}

function removeResult(index) {
    if (results[index] && results[index].url) {
        URL.revokeObjectURL(results[index].url);
    }
    results.splice(index, 1);
    if (results.length === 0) {
        clearResults();
    } else {
        const successes = results.filter(r => r.success).length;
        const failures = results.length - successes;
        let info = `${successes} file${successes !== 1 ? "s" : ""} converted`;
        if (failures > 0) info += `, ${failures} failed`;
        resultsInfo.textContent = info;
        renderResults();
    }
}

function openPreview(index) {
    const r = results[index];
    if (!r || !r.success) return;

    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <span class="modal-title">${r.name}</span>
                <div class="modal-actions">
                    <a class="btn-download" href="${r.url}" download="${r.name}">
                        <i data-lucide="download"></i> Download
                    </a>
                    <button class="btn-icon modal-close" title="Close">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            </div>
            <div class="modal-body">
                <iframe src="${r.url}"></iframe>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    lucide.createIcons();

    // Close handlers
    overlay.querySelector(".modal-close").addEventListener("click", () => overlay.remove());
    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) overlay.remove();
    });
    document.addEventListener("keydown", function escHandler(e) {
        if (e.key === "Escape") { overlay.remove(); document.removeEventListener("keydown", escHandler); }
    });
}

function clearResults() {
    results.forEach(r => { if (r.url) URL.revokeObjectURL(r.url); });
    results = [];
    resultsList.innerHTML = "";
    pdfPreview.src = "";
    showEmpty();
}

// ============================================================
// Event Handlers
// ============================================================

// Dropzone click
dropzone.addEventListener("click", (e) => {
    if (e.target !== selectFileBtn && !selectFileBtn.contains(e.target)) {
        fileInput.click();
    }
});

selectFileBtn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    fileInput.click();
});

// File input
fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) addFiles(e.target.files);
    fileInput.value = "";
});

// Drag and drop
dropzone.addEventListener("dragenter", (e) => { e.preventDefault(); dropzone.classList.add("active"); });
dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("active"); });
dropzone.addEventListener("dragleave", (e) => {
    e.preventDefault();
    if (!dropzone.contains(e.relatedTarget)) dropzone.classList.remove("active");
});
dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("active");
    if (e.dataTransfer.files.length > 0) addFiles(e.dataTransfer.files);
});

// Convert
convertBtn.addEventListener("click", convertFiles);

// Clear results
clearResultsBtn.addEventListener("click", clearResults);

// Fetch version
fetch("/api/health").then(r => r.json()).then(d => {
    versionBadge.textContent = "v" + d.version;
}).catch(() => {});

// Init lucide icons
lucide.createIcons();
