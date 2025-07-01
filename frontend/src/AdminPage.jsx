import { useState, useEffect } from "react";
import { apiFetch } from "./utils/apiFetch";

export default function AdminPage() {
  const [gliders, setGliders] = useState(null);
  const [newGlider, setNewGlider] = useState("");

  useEffect(() => {
    apiFetch("/gliders")
      .then((res) => res.json())
      .then((data) => setGliders(data))
      .catch((err) => {
        console.error("Failed to fetch gliders:", err);
        setGliders([]); // fallback to empty list
      });
  }, []);

  const handleAdd = async () => {
    const name = newGlider.trim();
    if (!name) return;

    const res = await apiFetch("/gliders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });

    if (res.ok) {
      setGliders((prev) => [...prev, name]);
      setNewGlider("");
    } else {
      alert("Failed to add glider.");
    }
  };

  const handleDelete = async (name) => {
    const res = await apiFetch(`/gliders/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });

    if (res.ok) {
      setGliders((prev) => prev.filter((g) => g !== name));
    } else {
      alert("Failed to delete glider.");
    }
  };

  return (
    <div style={{ padding: "1rem", fontFamily: "sans-serif" }}>
      <h1>Admin Page</h1>
      <p>Manage the list of gliders below:</p>

      {gliders === null ? (
        <p>Loading gliders...</p>
      ) : (
        <>
          <ul>
            {gliders.map((glider) => (
              <li key={glider}>
                {glider}{" "}
                <button onClick={() => handleDelete(glider)}>Delete</button>
              </li>
            ))}
          </ul>

          <input
            value={newGlider}
            onChange={(e) => setNewGlider(e.target.value)}
            placeholder="New glider name"
          />
          <button onClick={handleAdd}>Add Glider</button>
        </>
      )}
    </div>
  );
}
