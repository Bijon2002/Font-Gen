import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = import.meta.env.VITE_API || "http://127.0.0.1:8000";

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
  const [notice, setNotice] = useState("");

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
      setNotice(`${filename} is ready to use.`);
    } catch (requestError) {
      setError(requestError.message || "The request failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">F</span>
          <span>Font<span>Gen</span></span>
        </a>
        <span className="status-pill"><i /> Local workspace</span>
      </header>
      <main className="workspace">
        <section className="hero">
          <div className="eyebrow">TYPE, REIMAGINED</div>
          <h1>Make a font that<br /><em>sounds like you.</em></h1>
          <p>Turn handwriting and title art into a font you can install, share, and use anywhere.</p>
        </section>
        <section className="creator-card">
          <div className="card-heading">
            <div>
              <span className="section-kicker">FONT CREATOR</span>
              <h2>Build your typeface</h2>
            </div>
            <span className="step-count">01 / 03</span>
          </div>
          <div className="stepper">
            <span className="active"><b>1</b> Choose a source</span>
            <span><b>2</b> Tune the details</span>
            <span><b>3</b> Export</span>
          </div>
          <div className="mode-grid">
            <button className={`mode-card ${mode === "template" ? "selected" : ""}`} onClick={() => setMode("template")}>
              <span className="mode-icon">Aa</span>
              <span><strong>Handwriting</strong><small>Fill a printable template</small></span>
              <span className="radio" />
            </button>
            <button className={`mode-card ${mode === "style" ? "selected" : ""}`} onClick={() => setMode("style")}>
              <span className="mode-icon style-icon">✦</span>
              <span><strong>Style from image</strong><small>Match a title design</small></span>
              <span className="radio" />
            </button>
          </div>
          {mode === "template" && (
            <div className="helper-row">
              <span>Need the worksheet first?</span>
              <a href={`${API}/template`} download>Download template <span>↗</span></a>
            </div>
          )}
          <label className="upload-zone">
            <input type="file" accept="image/*" onChange={(event) => { setFile(event.target.files[0] || null); setError(""); setNotice(""); }} />
            <span className="upload-icon">↑</span>
            <strong>{file ? file.name : "Drop your image here"}</strong>
            <small>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB selected` : "or click to browse · PNG, JPG up to 10 MB"}</small>
          </label>
          <div className="fields-row">
            <label>Font name<input value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Sunday Morning" /></label>
            {mode === "style" && <label>Text in image<input value={word} onChange={(event) => setWord(event.target.value)} placeholder="e.g. SCENE" /></label>}
          </div>
          {mode === "style" && file && <>
            <div className="picker-label"><span>Pick the face color from your image</span><span className="swatch" style={{ background: color }}>{color}</span></div>
            <PickColor file={file} onPick={setColor} />
          </>}
          <div className="actions">
            <button className="primary-button" disabled={busy} onClick={() => download("/generate", `${name || "FontGen"}.ttf`, { name, mode, text: word, color })}>
              {busy ? "Creating your font..." : "Generate TTF"} <span>→</span>
            </button>
            <button className="secondary-button" disabled={busy} onClick={() => download("/cutout", "title.png")}>Export title PNG</button>
          </div>
          {notice && <p className="notice">{notice}</p>}
          {error && <p className="error">{error}</p>}
        </section>
        <p className="privacy-note"><span>✦</span> Your images stay on your machine while running locally.</p>
      </main>
      <footer>FontGen <span>·</span> Make something original.</footer>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
