export function getBackendBaseUrl() {
  const backendUrl =
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    (process.env.NODE_ENV === 'development' ? process.env.NEXT_PUBLIC_API_URL : '') ||
    'http://localhost:8000';
  const normalizedUrl = backendUrl.trim().replace(/\/$/, '');

  if (!normalizedUrl) {
    throw new Error(
      'Missing backend API URL. Set BACKEND_API_URL in the frontend deployment environment.'
    );
  }

  return normalizedUrl;
}

export async function proxyJsonRequest(path, options = {}) {
  const response = await fetch(`${getBackendBaseUrl()}${path}`, options);
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    return Response.json(
      {
        error: data?.error || data?.detail || `Backend returned ${response.status}`,
      },
      { status: response.status }
    );
  }

  return Response.json(data);
}