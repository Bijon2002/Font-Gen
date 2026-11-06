import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = import.meta.env.VITE_API || "http://localhost:8000";

function PickColor({ file, onPick }) {
  const ref = useRef(null);
  useEffect(() => {
    const image = new Image();
    const url = URL.createObjectURL(file);
    image.onload = () => {
      const canvas = ref.current;
      canvas.width = image.width;
      canvas.height = image.height;
      canvas.getContext("2d").drawImage(image, 0, 0);
      URL.revokeObjectURL(url);
    };
    image.src = url;
    return () => URL.revokeObjectURL(url);
  }, [file]);
  const pick = (event) => {
    const canvas = ref.current;
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor(((event.clientX - rect.left) * canvas.width) / rect.width);
    const y = Math.floor(((event.clientY - rect.top) * canvas.height) / rect.height);
    const [r, g, b] = canvas.getContext("2d").getImageData(x, y, 1, 1).data;
    onPick(`#${[r, g, b].map((value) => value.toString(16).padStart(2, "0")).join("")}`);
  };
  return <canvas ref={ref} onClick={pick} />;
}

function App() {
  const [mode, setMode] = useState("template");
  const [file, setFile] = useState(null);
  const [name, setName] = useState("FontGen");
  const [word, setWord] = useState("");
  const [color, setColor] = useState("#f5b800");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const download = async (endpoint, filename, fields = {}) => {
    if (!file) return setError("Choose an image first.");
    setBusy(true);
    setError("");
    try {
      const form = new FormData();
      form.append("photo", file);
      Object.entries(fields).forEach(([key, value]) => form.append(key, value));
      const response = await fetch(`${API}${endpoint}`, { method: "POST", body: form });
      if (!response.ok) throw new Error(await response.text());
      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (requestError) {
      setError(requestError.message || "The request failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main>
      <h1>FontGen</h1>
      <p>Turn handwriting or a title image into a font.</p>
      <a href={`${API}/template`} download>Download handwriting template</a>
      <label>Mode<select value={mode} onChange={(event) => setMode(event.target.value)}>
        <option value="template">Handwriting template</option>
        <option value="ai">AI from template</option>
        <option value="style">Style from image</option>
      </select></label>
      <label>Image<input type="file" accept="image/*" onChange={(event) => setFile(event.target.files[0] || null)} /></label>
      <label>Font name<input value={name} onChange={(event) => setName(event.target.value)} /></label>
      {mode === "style" && file && <>
        <p>Click the letter face color:</p>
        <PickColor file={file} onPick={setColor} />
        <label>Text in image<input value={word} onChange={(event) => setWord(event.target.value)} placeholder="SCENE" /></label>
        <span className="swatch" style={{ background: color }}>{color}</span>
      </>}
      <div className="actions">
        <button disabled={busy} onClick={() => download("/generate", `${name || "FontGen"}.ttf`, { name, mode, text: word, color })}>
          {busy ? "Working..." : "Generate TTF"}
        </button>
        <button disabled={busy} onClick={() => download("/cutout", "title.png")}>Download title PNG</button>
      </div>
      {error && <p className="error">{error}</p>}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
