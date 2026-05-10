export async function POST(request) {
  try {
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    const payload = await request.text();
    const response = await fetch(`${backendUrl}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload,
    });

    if (!response.ok) {
      return Response.json({ error: `Backend returned ${response.status}` }, { status: response.status });
    }

    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
