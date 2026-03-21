import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";

export const { handlers, auth, signIn, signOut } = NextAuth({
    providers: [
        GitHub({
            clientId: process.env.GITHUB_CLIENT_ID ?? "",
            clientSecret: process.env.GITHUB_CLIENT_SECRET ?? "",
        }),
        Google({
            clientId: process.env.GOOGLE_CLIENT_ID ?? "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
        }),
    ],
    session: { strategy: "jwt" },
    pages: { signIn: "/login" },
    callbacks: {
        jwt({ token, user, account }) {
            if (user) {
                token.id = user.id ?? account?.providerAccountId ?? user.email;
                token.provider = account?.provider;
            }
            return token;
        },
        session({ session, token }) {
            if (session.user) {
                (session.user as any).id = token.id as string;
                (session.user as any).provider = token.provider as string;
            }
            return session;
        },
    },
    secret: process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET,
    trustHost: true,
});
