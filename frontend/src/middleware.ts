import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/", "/chat-bot", "/url/documets"];
const publicRoutes = ["/login"];

export function middleware(request: NextRequest) {
  const sessionId = request.cookies.get("sessionid")?.value;
  const { pathname } = request.nextUrl;

  if (protectedRoutes.includes(pathname) && !sessionId) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (publicRoutes.includes(pathname) && sessionId) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}
