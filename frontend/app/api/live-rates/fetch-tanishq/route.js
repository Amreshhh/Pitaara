export async function GET(request) {
  try {
    const backendUrl = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL;
    
    if (!backendUrl) {
      return Response.json(
        { error: 'Backend API URL not configured' },
        { status: 500 }
      );
    }

    // Prevent frontend from calling itself
    const frontendHost = new URL(request.url).host;
    const backendHost = new URL(backendUrl).host;
    
    if (frontendHost === backendHost) {
      return Response.json(
        { error: 'Invalid configuration: Frontend calling itself' },
        { status: 500 }
      );
    }

    console.log('[fetch-tanishq] Proxying to backend:', `${backendUrl}/api/live-rates/fetch-tanishq`);

    // Proxy request to Python backend
    const response = await fetch(`${backendUrl}/api/live-rates/fetch-tanishq`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[fetch-tanishq] Backend error:', response.status, errorText);
      return Response.json(
        { error: `Backend returned ${response.status}`, details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('[fetch-tanishq] Success:', data.message);
    
    return Response.json(data);
  } catch (error) {
    console.error('[fetch-tanishq] Proxy error:', error);
    return Response.json(
      { error: error.message || 'Failed to fetch Tanishq rates' },
      { status: 500 }
    );
  }
}
