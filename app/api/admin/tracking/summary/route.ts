import { NextResponse } from 'next/server';
import { AdminAuthService } from '@/lib/auth/adminAuth';
import { getTrackingSummary, parseDaysParam } from '@/lib/dreamweaverTracking/admin';

export async function GET(request: Request) {
  try {
    const authError = await AdminAuthService.protectRoute(request, {
      mode: 'admin',
    });
    if (authError) return authError;

    const { searchParams } = new URL(request.url);
    const days = parseDaysParam(searchParams.get('days'));

    const summary = await getTrackingSummary(days);
    return NextResponse.json(summary);
  } catch (error) {
    console.error('Error fetching tracking summary:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch tracking summary',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

