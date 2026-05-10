export async function GET(request, { params }) {
  try {
    const { category } = params;
    const backendUrl =
      process.env.BACKEND_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_API_URL ||
      (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '');

    if (!backendUrl) {
      return Response.json(
        { error: 'Backend API URL is not configured. Set BACKEND_API_URL on deployment.' },
        { status: 503 }
      );
    }

    const response = await fetch(
      `${backendUrl}/api/inventory-matrix/${encodeURIComponent(category)}`
    );
    
    if (!response.ok) {
      return Response.json(
        { error: `Backend returned ${response.status}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
