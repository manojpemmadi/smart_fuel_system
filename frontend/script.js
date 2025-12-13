// script.js
const form = document.getElementById("uploadForm");
const status = document.getElementById("status");
const results = document.getElementById("results");
const jsonOut = document.getElementById("jsonOut");
const visual = document.getElementById("visual");
const submitBtn = document.getElementById("submitBtn");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  results.style.display = "none";
  jsonOut.textContent = "";
  visual.innerHTML = "";
  status.textContent = "Uploading and processing...";

  const fileInput = document.getElementById("imageInput");
  if (!fileInput.files || fileInput.files.length === 0) {
    status.textContent = "Please select an image first.";
    return;
  }

  const file = fileInput.files[0];
  if (file.size > 10 * 1024 * 1024) {
    status.textContent = "File too large (max 10 MB).";
    return;
  }

  const formData = new FormData();
  formData.append("image", file);

  submitBtn.disabled = true;
  try {
    const res = await fetch("/predict", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (!res.ok) {
      status.textContent = `Error: ${data.error || res.statusText}`;
      submitBtn.disabled = false;
      return;
    }

    status.textContent = "Done.";
    results.style.display = "block";
    jsonOut.textContent = JSON.stringify(data, null, 2);

    if (data.visualization_base64) {
      const imgEl = document.createElement("img");
      imgEl.src = "data:image/jpeg;base64," + data.visualization_base64;
      visual.appendChild(imgEl);
    } else {
      visual.textContent = "No visualization available (no detections).";
    }
  } catch (err) {
    status.textContent = "Request failed: " + err;
  } finally {
    submitBtn.disabled = false;
  }
});
