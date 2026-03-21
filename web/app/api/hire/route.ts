import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { name, email, company, budget, project } = body;

        if (!name || !email || !project) {
            return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
        }

        const { error } = await supabase
            .from('hire_inquiries')
            .insert([
                { name, email, company, budget, project }
            ]);

        if (error) {
            console.error('Supabase error:', error);
            return NextResponse.json({ error: 'Database error' }, { status: 500 });
        }

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('API /hire error:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
