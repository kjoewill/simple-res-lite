export function apiFetch(path, options = {}) {
  const base = window.__API_URL__ || '';
  const fullPath = `${base}/api${path.startsWith('/') ? path : '/' + path}`;
  return fetch(fullPath, options).then((res) => {
    if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
    return res;
  });
}
