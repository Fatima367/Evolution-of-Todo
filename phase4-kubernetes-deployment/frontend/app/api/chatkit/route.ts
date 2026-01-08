import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  // Get the API URL from environment variables
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const chatkitUrl = `${backendUrl}/chatkit`;

  try {
    // Get the auth token from the request headers
    const authHeader = request.headers.get('authorization');
    const contentType = request.headers.get('content-type');

    // Prepare the request to forward to the backend
    const body = await request.text();

    const response = await fetch(chatkitUrl, {
      method: 'POST',
      headers: {
        'Content-Type': contentType || 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
      body: body,
    });

    // Get response headers
    const responseHeaders = new Headers(response.headers);
    // Ensure proper content type for streaming responses
    if (responseHeaders.get('content-type')?.includes('text/event-stream')) {
      responseHeaders.set('Content-Type', 'text/event-stream');
      responseHeaders.set('Cache-Control', 'no-cache');
      responseHeaders.set('Connection', 'keep-alive');
      responseHeaders.set('X-Accel-Buffering', 'no');
    } else {
      responseHeaders.set('Content-Type', response.headers.get('content-type') || 'application/json');
    }

    // Return the response from the backend
    const responseText = await response.text();

    return new NextResponse(responseText, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('ChatKit API proxy error:', error);
    return new NextResponse(
      JSON.stringify({ error: 'Failed to connect to ChatKit service' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

export async function GET() {
  // Health check endpoint
  return NextResponse.json({ status: 'healthy', service: 'chatkit-proxy' });
}