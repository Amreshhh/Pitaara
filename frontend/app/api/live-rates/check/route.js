export async function GET() {
	try {
		const backendUrl = 'https://pitaara-xz2s-git-v2-development-amreshhhs-projects.vercel.app' || process.env.NEXT_PUBLIC_API_URL;
		if (!backendUrl) {
			return Response.json(
				{ error: 'Missing BACKEND_API_URL or NEXT_PUBLIC_API_URL' },
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