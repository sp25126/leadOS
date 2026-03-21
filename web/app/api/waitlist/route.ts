import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { email, product } = body;

        if (!email || !product) {
            return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
        }

        const { error } = await supabase
            .from('waitlist')
            .insert([
                { email, product }
            ]);

        if (error) {
            // If error is unique constraint, ignore or return success anyway
            if (error.code === '23505') {
                return NextResponse.json({ success: true, message: 'Already on waitlist' });
            }
            console.error('Supabase error:', error);
            return NextResponse.json({ error: 'Database error' }, { status: 500 });
        }

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('API /waitlist error:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
