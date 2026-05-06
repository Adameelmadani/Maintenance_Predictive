/**
 * API service module — centralised fetch wrapper for the Flask backend.
 */

const API_BASE = '/api';

async function fetchJSON(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  getOverview:    ()          => fetchJSON('/overview'),
  getKPIs:        ()          => fetchJSON('/kpis'),
  getEngines:     ()          => fetchJSON('/engines'),
  getEngine:      (id)        => fetchJSON(`/engine/${id}`),
  getMonitoring:  (id, sensor, window) =>
    fetchJSON(`/monitoring/${id}?sensor=${encodeURIComponent(sensor)}&window=${window}`),
  getBenchmarks:  ()          => fetchJSON('/benchmarks'),
  predict:        (engineId, model) =>
    fetchJSON('/predict', {
      method: 'POST',
      body: JSON.stringify({ engine_id: engineId, model }),
    }),
};
