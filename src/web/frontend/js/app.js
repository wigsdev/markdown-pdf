/**
 * MDPDF Web Interface
 */

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const selectFileBtn = document.getElementById("selectFileBtn");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFileBtn = document.getElementById("removeFileBtn");
const styleSelect = document.getElementById("styleSelect");
const tocToggle = document.getElementById("tocToggle");
const tocLevel = document.getElementById("tocLevel");
const convertBtn = document.getElementById("convertBtn");
const statusSection = document.getElementById("statusSection");
const statusText = document.getElementById("statusText");
const successSection = document.getElementById("successSection");
const successInfo = document.getElementById("successInfo");
const downloadBtn = document.getElementById("downloadBtn");
const errorSection = document.getElementById("errorSection");
const errorMessage = document.getElementById("errorMessage");
const convertAnotherBtn = document.getElementById("convertAnotherBtn");
const retryBtn = document.getElementById("retryBtn");

let selectedFile = null;
let blobUrl = null;

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

function hideAll() {
    statusSection.hidden = true;
    successSection.hidden = true;
    errorSection.hidden = true;
}

function reset() {
    selectedFile = null;
    fileInput.value = "";
    fileInfo.hidden = true;
    convertBtn.disabled = true;
    if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
        blobUrl = null;
    }
    hideAll();
}

function selectFile(file) {
    const valid = [".md", ".markdown", ".mdown", ".mkd", ".mkdn"];
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!valid.includes(ext)) {
        showError("Invalid file. Allowed: " + valid.join(", "));
        return;
    }
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatSize(file.size);
    fileInfo.hidden = false;
    convertBtn.disabled = false;
    hideAll();
}

function showError(msg) {
    hideAll();
    errorMessage.textContent = msg;
    errorSection.hidden = false;
}

// ============================================================
// Events
// ============================================================

dropzone.addEventListener("click", (e) => {
    if (e.target !== selectFileBtn) fileInput.click();
});

selectFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
});

fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) selectFile(e.target.files[0]);
});

dropzone.addEventListener("dragenter", (e) => {
    e.preventDefault();
    dropzone.classList.add("active");
});

dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("active");
});

dropzone.addEventListener("dragleave", (e) => {
    e.preventDefault();
    if (!dropzone.contains(e.relatedTarget)) {
        dropzone.classList.remove("active");
    }
});

dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("active");
    if (e.dataTransfer.files.length > 0) selectFile(e.dataTransfer.files[0]);
});

removeFileBtn.addEventListener("click", reset);
convertAnotherBtn.addEventListener("click", reset);
retryBtn.addEventListener("click", () => { hideAll(); });

convertBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    hideAll();
    statusSection.hidden = false;
    statusText.textContent = "Converting...";
    convertBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("style", styleSelect.value);
        formData.append("toc", tocToggle.checked);
        formData.append("toc_level", tocLevel.value);

        const response = await fetch("/api/convert", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Server error: " + response.status);
        }

        const buffer = await response.arrayBuffer();
        const blob = new Blob([buffer], { type: "application/pdf" });

        if (blob.size === 0) {
            throw new Error("Generated PDF is empty");
        }

        blobUrl = URL.createObjectURL(blob);
        const pdfName = selectedFile.name.replace(/\.(md|markdown|mdown|mkd|mkdn)$/i, ".pdf");

        downloadBtn.href = blobUrl;
        downloadBtn.download = pdfName;
        successInfo.textContent = pdfName + " (" + formatSize(blob.size) + ")";

        hideAll();
        successSection.hidden = false;

    } catch (err) {
        showError(err.message || "An error occurred");
    } finally {
        convertBtn.disabled = !selectedFile;
    }
});
