const API_URL = "http://127.0.0.1:8000"; // asegúrate que coincida con el backend

async function clasificarTexto() {
  const texto = document.getElementById("texto").value.trim();
  const predElem = document.getElementById("prediccion");
  const probElem = document.getElementById("probabilidad");

  if (!texto) {
    predElem.textContent = "Por favor ingresa un texto antes de clasificar.";
    return;
  }

  try {
    const response = await fetch(`${API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ instances: [{ textos: texto }] })
    });

    if (!response.ok) throw new Error("Error en la respuesta del servidor");

    const data = await response.json();
    const item = data.predictions[0];

    predElem.textContent = `Predicción: ${item.label_name} (ODS ${item.label})`;
    probElem.textContent = item.prob
      ? `Probabilidad: ${(item.prob * 100).toFixed(2)}%`
      : "Probabilidad no disponible.";
  } catch (error) {
    predElem.textContent = "Error al clasificar el texto.";
    console.error(error);
  }
}

async function reentrenarDesdeArchivo() {
  const input = document.getElementById("fileInput");
  const file = input.files[0];
  const predElem = document.getElementById("prediccion");
  const probElem = document.getElementById("probabilidad");

  if (!file) {
    alert("Por favor selecciona un archivo .xlsx o .json");
    return;
  }

  try {
    let data = [];

    if (file.name.endsWith(".json")) {
      const text = await file.text();
      const json = JSON.parse(text);

      data = json.map(item => ({
        textos: item.textos || item.text || item.Texto || item.Comentario || "",
        labels: parseInt(item.labels || item.ODS || item.Clasificacion || 0)
      }));

    } else if (file.name.endsWith(".xlsx")) {
      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const json = XLSX.utils.sheet_to_json(sheet);

      data = json.map(row => ({
        textos: row.textos || row.Texto || row.Comentario || "",
        labels: parseInt(row.labels || row.ODS || row.Clasificacion || 0)
      }));
    }

    if (data.length < 30) {
      alert("El backend requiere al menos 30 registros. Tienes: " + data.length);
      return;
    }

    const response = await fetch(`${API_URL}/retrain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ instances: data })
    });

    const res = await response.json();

    if (!response.ok) throw new Error(JSON.stringify(res.detail || res));

    predElem.textContent = "Modelo reentrenado exitosamente.";
    probElem.textContent = `F1: ${res.f1.toFixed(3)} | Precision: ${res.precision.toFixed(
      3
    )} | Recall: ${res.recall.toFixed(3)}`;
  } catch (err) {
    predElem.textContent = "❌ Error al reentrenar el modelo.";
    console.error("Error en reentrenamiento:", err);
  }
}
