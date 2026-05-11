// export async function GET(request) {
//   try {
//     const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
//     const response = await fetch(`${backendUrl}/api/inventory-categories`);
    
//     if (!response.ok) {
//       return Response.json(
//         { error: `Backend returned ${response.status}` },
//         { status: response.status }
//       );
//     }
    
//     const data = await response.json();
//     return Response.json(data);
//   } catch (error) {
//     return Response.json(
//       { error: error.message },
//       { status: 500 }
//     );
//   }
// }
