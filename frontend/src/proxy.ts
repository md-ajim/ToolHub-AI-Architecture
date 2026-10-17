import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;

  const isAuthPage = request.nextUrl.pathname.startsWith('/login') || 
                     request.nextUrl.pathname.startsWith('/register') ||
                     request.nextUrl.pathname.startsWith('/forgot-password') ||
                     request.nextUrl.pathname.startsWith('/reset-password') ||
                     request.nextUrl.pathname.startsWith('/verify-email') ||
                     request.nextUrl.pathname === '/auth' ||
                     request.nextUrl.pathname.startsWith('/auth/');
  
  const isDashboardPage = request.nextUrl.pathname.startsWith('/dashboard');
  // Public AI discovery pages remain indexable; only workspace conversations/compare/projects require auth
  const isPublicAiRoute = request.nextUrl.pathname === '/ai/models' || request.nextUrl.pathname.startsWith('/ai/models/');
  const isAiWorkspacePage = (request.nextUrl.pathname === '/ai' || request.nextUrl.pathname.startsWith('/ai/')) && !isPublicAiRoute;

  if (!token && (isDashboardPage || isAiWorkspacePage)) {
    const url = new URL('/login', request.url);
    url.searchParams.set('next', request.nextUrl.pathname + request.nextUrl.search);
    return NextResponse.redirect(url);
  }

  if (token && isAuthPage) {
    // Respect ?next= for already-authenticated users, else go to workspace
    const next = request.nextUrl.searchParams.get('next');
    if (next && next.startsWith('/') && !next.startsWith('//')) {
      return NextResponse.redirect(new URL(next, request.url));
    }
    return NextResponse.redirect(new URL('/ai', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard', '/dashboard/:path*', '/ai', '/ai/:path*', '/login', '/register', '/forgot-password', '/reset-password', '/verify-email', '/auth', '/auth/:path*'],
};
