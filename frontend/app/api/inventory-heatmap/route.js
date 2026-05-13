export async function GET(request) {
  try {
    const backendUrl = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const frontendHost = new URL(request.url).host;
    const backendHost = new URL(backendUrl).host;
    if (frontendHost === backendHost) {
      return Response.json(
        { error: 'Misconfigured backend URL: frontend is calling itself. Set BACKEND_API_URL to backend project domain.' },
        { status: 500 }
      );
    }
    const url = new URL(request.url);
    const search = url.search; // preserve query params (category, purity)

    const response = await fetch(`${backendUrl}/api/inventory-heatmap${search}`);

    if (!response.ok) {
      return Response.json(
        { error: `Backend returned ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
