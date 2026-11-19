(() => {
  const form = document.getElementById("report-form");
  const button = document.getElementById("analyze-photo");
  const result = document.getElementById("ai-result");
  const photoInput = document.getElementById("report-photo");
  if (!form || !button || !result || !photoInput) return;
  const suggestionFields = [
    form.elements.item_name,
    form.elements.category,
    form.elements.item_type,
    form.elements.color,
  ];

  suggestionFields.forEach((field) => {
    field.addEventListener("input", () => {
      delete field.dataset.aiSuggested;
    });
  });

  const clearPreviousSuggestions = () => {
    suggestionFields.forEach((field) => {
      if (field.dataset.aiSuggested === "true") {
        field.value = "";
        delete field.dataset.aiSuggested;
      }
    });
  };

  const applySuggestion = (field, value) => {
    if (value && (!field.value || field.dataset.aiSuggested === "true")) {
      field.value = value;
      field.dataset.aiSuggested = "true";
    }
  };

  const analyzePhoto = async () => {
    if (button.disabled) return;
    if (!photoInput.files.length) {
      result.textContent = "Choose an image first.";
      return;
    }

    button.disabled = true;
    clearPreviousSuggestions();
    result.textContent = "Analyzing the image on this server…";
    try {
      const response = await fetch(form.dataset.aiUrl, {
        method: "POST",
        body: new FormData(form),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || "Image analysis failed.");
      applySuggestion(form.elements.item_name, data.item_name);
      applySuggestion(form.elements.category, data.category);
      applySuggestion(form.elements.item_type, data.item_type);
      applySuggestion(form.elements.color, data.color);
      const detections = data.detections.map((item) =>
        `${item.label} (${Math.round(item.confidence * 100)}%)`,
      ).join(", ");
      result.textContent = detections ? `${data.notice} Detected: ${detections}` : data.notice;
    } catch (error) {
      result.textContent = error.message || "Image analysis failed. Enter details manually.";
    } finally {
      button.disabled = false;
    }
  };

  photoInput.addEventListener("change", analyzePhoto);
  button.addEventListener("click", analyzePhoto);
})();
