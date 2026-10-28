import { useState, useRef } from "react";

export default function ImageUpload({ label, accept, onFile, maxSizeMB = 10 }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleChange = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setError(null);
    if (maxSizeMB && f.size > maxSizeMB * 1024 * 1024) {
      setError(`File too large. Maximum ${maxSizeMB} MB.`);
      return;
    }
    setFile(f);
    if (onFile) onFile(f);
  };

  const remove = () => {
    setFile(null);
    setError(null);
  };

  return (
    <div className="field">
      <label>{label}</label>
      <div className="upload-zone" onClick={() => inputRef.current.click()}>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
        />
        {file ? (
          <>
            <p style={{ color: "#16a34a", margin: 0 }}>\u2713 {file.name}</p>
            <button
              onClick={remove}
              className="btn btn-danger btn-sm"
              style={{ marginTop: 8 }}
            >
              Remove
            </button>
          </>
        ) : (
          <p style={{ margin: 0 }}>Click to upload {label.toLowerCase()}</p>
        )}
      </div>
      {error && <div className="alert alert-error" style={{ marginTop: 6 }}>{error}</div>}
    </div>
  );
}
