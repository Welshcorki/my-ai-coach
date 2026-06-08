import { useState, useEffect } from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { supabase } from '../lib/supabaseClient.ts';

interface UseAuthResult {
    session: Session | null;
    user: User | null;
    loading: boolean;
    signInWithGoogle: () => Promise<void>;
    signOut: () => Promise<void>;
}

/**
 * Supabase 인증 세션을 관리하는 훅.
 * - 초기 세션 로드 + onAuthStateChange 구독으로 세션 상태를 동기화한다.
 */
export function useAuth(): UseAuthResult {
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        // 1. 초기 세션 로드 (새로고침/콜백 복귀 시 복원)
        supabase.auth.getSession().then(({ data }) => {
            setSession(data.session);
            setLoading(false);
        });

        // 2. 로그인/로그아웃/토큰갱신 등 상태 변화 구독
        const { data: subscription } = supabase.auth.onAuthStateChange((_event, newSession) => {
            setSession(newSession);
        });

        return () => {
            subscription.subscription.unsubscribe();
        };
    }, []);

    const signInWithGoogle = async () => {
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: { redirectTo: window.location.origin },
        });
        if (error) {
            console.error('Google 로그인 실패:', error.message);
            alert(`로그인 중 오류가 발생했습니다: ${error.message}`);
        }
    };

    const signOut = async () => {
        await supabase.auth.signOut();
    };

    return {
        session,
        user: session?.user ?? null,
        loading,
        signInWithGoogle,
        signOut,
    };
}
