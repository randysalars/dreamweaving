import { NextResponse } from 'next/server';
import { AdminAuthService } from '@/lib/auth/adminAuth';
import { getSessionDetail } from '@/lib/dreamweaverTracking/admin';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const authError = await AdminAuthService.protectRoute(request, {
      mode: 'admin',
    });
    if (authError) return authError;

    const { sessionId } = await params;
    if (!sessionId || typeof sessionId !== 'string') {
      return NextResponse.json({ error: 'Missing sessionId' }, { status: 400 });
    }

    const detail = await getSessionDetail(sessionId);
    if (!detail.session) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 });
    }

    return NextResponse.json(detail);
  } catch (error) {
    console.error('Error fetching tracking session detail:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch tracking session detail',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

