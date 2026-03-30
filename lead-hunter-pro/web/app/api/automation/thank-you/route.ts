import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { name, email } = await req.json();

        // Template for the gratitude message
        const message = `
Hello ${name},

Thank you so much for visiting Octagon and exploring my work! 🚀

I'm Saumya Patel, the architect behind these engines. I'd love to hear your thoughts on the tools you explored. If you have a moment, could you share a review or connect with me on LinkedIn?

LinkedIn: https://linkedin.com/in/saumya-patel-architect
Portfolio: https://saumyapatel.me

I'm also open for specialized MVP builds if you have a unique concept in mind.

Best regards,
Saumya Patel
        `;

        // Logic to send email/message via Brevo or a generic provider would go here
        // For now, we simulate and log for the user to see the personalized outcome
        // Automation: Thank You sent

        return NextResponse.json({ 
            success: true, 
            message: "Gratitude protocol initiated." 
        });
    } catch (e) {
        return NextResponse.json({ error: "Failed to process gratitude" }, { status: 500 });
    }
}
