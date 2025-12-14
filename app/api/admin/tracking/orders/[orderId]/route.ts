import { NextResponse } from 'next/server';
import { AdminAuthService } from '@/lib/auth/adminAuth';
import { getOrderDetail } from '@/lib/dreamweaverTracking/admin';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ orderId: string }> }
) {
  try {
    const authError = await AdminAuthService.protectRoute(request, {
      mode: 'admin',
    });
    if (authError) return authError;

    const { orderId } = await params;
    if (!orderId || typeof orderId !== 'string') {
      return NextResponse.json({ error: 'Missing orderId' }, { status: 400 });
    }

    const detail = await getOrderDetail(orderId);
    if (!detail.order) {
      return NextResponse.json({ error: 'Order not found' }, { status: 404 });
    }

    return NextResponse.json(detail);
  } catch (error) {
    console.error('Error fetching tracking order detail:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch tracking order detail',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

