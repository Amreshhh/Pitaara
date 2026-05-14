export async function GET(request) {
	try {
		const backendUrl = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL;
		if (!backendUrl) {
			return Response.json(
				{ error: 'Missing BACKEND_API_URL or NEXT_PUBLIC_API_URL' },
				{ status: 500 }
			);
		}
		const frontendHost = new URL(request.url).host;
		const backendHost = new URL(backendUrl).host;
		if (frontendHost === backendHost) {
			return Response.json(
				{ error: 'Misconfigured backend URL: frontend is calling itself. Set BACKEND_API_URL to backend project domain.' },
				{ status: 500 }
			);
		}

		const response = await fetch(`${backendUrl}/api/live-rates/check`, {
			cache: 'no-store',
		});

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