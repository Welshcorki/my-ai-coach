import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

if (!supabaseUrl || !supabaseAnonKey) {
    // 빌드/런타임 설정 누락을 조기에 드러내기 위한 경고
    console.error(
        'Supabase 환경변수가 설정되지 않았습니다. frontend/.env 에 VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY 를 설정하세요.'
    );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
