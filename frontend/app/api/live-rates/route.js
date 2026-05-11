export async function GET() {
	try {
		const backendUrl = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
		const response = await fetch(`${backendUrl}/api/live-rates`, {
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
