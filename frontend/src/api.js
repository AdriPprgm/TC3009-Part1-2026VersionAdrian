const API_BASE = `http://${window.location.hostname}:8080`;

async function get(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`);

  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") return;
    url.searchParams.set(key, String(value));
  });

  const respuesta = await fetch(url, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!respuesta.ok) {
    let payload = {};
    try {
      payload = await respuesta.json();
    } catch {
      // Ignoramos errores de parsing: el cuerpo puede no ser JSON.
    }

    const mensaje = payload?.error || `${respuesta.status} ${respuesta.statusText}`;
    throw new Error(mensaje);
  }

  return respuesta.json();
}

export function getHealth() {
  return get("/api/health");
}

export function getStats(neighborhood = "") {
  const params = neighborhood ? { neighborhood } : {};
  return get("/api/stats", params);
}

export function getData(neighborhood = "", limit = 20) {
  const params = {
    ...(neighborhood ? { neighborhood } : {}),
    limit,
  };
  return get("/api/data", params);
}

