import { auth } from "@/auth"
import { NextResponse } from "next/server"

export default auth((req) => {
  const { nextUrl } = req
  const isLoggedIn = !!req.auth
  const isLeados = nextUrl.pathname.startsWith("/leados")
  const isLegacy = ["/leads", "/outreach", "/settings"].some(p => nextUrl.pathname.startsWith(p))
  
  if (isLegacy) {
    const newPath = `/leados${nextUrl.pathname}`
    return NextResponse.redirect(new URL(newPath, nextUrl))
  }

  if (isLeados && !isLoggedIn) {
    return NextResponse.redirect(new URL("/login", nextUrl))
  }

  return NextResponse.next()
})

export const config = {
  matcher: [
    "/leados/:path*",
    "/settings/:path*",
    "/leads/:path*",
    "/outreach/:path*",
  ],
}
