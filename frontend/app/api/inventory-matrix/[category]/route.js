export async function GET(request, { params }) {
  try {
    const { category } = params;
    const backendUrl = 'https://pitaara-xz2s-git-v2-development-amreshhhs-projects.vercel.app' || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
