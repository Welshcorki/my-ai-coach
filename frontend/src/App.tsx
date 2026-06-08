import React, { useState, useCallback, useEffect } from 'react';
import { Roadmap, ChatMessage, RoadmapSummary } from './types.ts';
import SetupScreen from './components/SetupScreen.tsx';
import Dashboard from './components/Dashboard.tsx';
import LoginScreen from './components/LoginScreen.tsx';
import { ArrowLeftOnRectangleIcon } from './components/Icons.tsx';
import { useAuth } from './hooks/useAuth.ts';
import { generateRoadmap, getAllRoadmaps, getRoadmapDetail } from './hooks/useGemini.ts';

const App: React.FC = () => {
    const { session, loading: authLoading, signInWithGoogle, signOut } = useAuth();
    const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [roadmapList, setRoadmapList] = useState<RoadmapSummary[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // 로그인(세션 존재) 이후에만 학습 목록 로드
    useEffect(() => {
        if (session) {
            loadRoadmapList();
        }
    }, [session]);

    const loadRoadmapList = async () => {
        try {
            const list = await getAllRoadmaps();
            setRoadmapList(list);
        } catch (err) {
            console.log("Failed to load roadmap list:", err);
        }
    };

    const handleLoadRoadmap = async (id: number) => {
        setIsLoading(true);
        setError(null);
        try {
            const detail = await getRoadmapDetail(id);
            setRoadmap(detail);
            setMessages(detail.chat_history || []);
        } catch (err) {
            console.error(err);
            alert("로드맵 데이터를 불러오는 중 오류가 발생했습니다.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateRoadmap = useCallback(async (goal: string, level: string, duration: number, frequency: string, file?: File | null) => {
        setIsLoading(true);
        setError(null);
        try {
            const newRoadmap = await generateRoadmap(goal, level, duration, frequency, file);
            setRoadmap(newRoadmap);
            // 새 로드맵 생성 시 초기 메시지
            setMessages([{ 
                id: 'init', 
                role: 'model', 
                text: `안녕하세요! 저는 당신의 AI 코치 'Grow'입니다. **${newRoadmap.project_title}** 학습 로드맵이 준비되었습니다. 함께 시작해볼까요? 무엇이 궁금하신가요?` 
            }]);
            // 목록 갱신 (백그라운드)
            loadRoadmapList();
        } catch (err) {
            console.error(err);
            setError(err instanceof Error ? err.message : '로드맵을 생성하는 중 알 수 없는 오류가 발생했습니다.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const handleReset = () => {
        if (window.confirm("현재 화면을 닫고 메인 목록으로 돌아가시겠습니까?")) {
            setRoadmap(null);
            setMessages([]);
            setError(null);
            loadRoadmapList(); // 목록 최신화
        }
    };

    // 세션 확인 중: 로딩 스피너
    if (authLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#0f0c29] via-[#1a1a2e] to-[#1c1c3c]">
                <svg className="animate-spin h-8 w-8 text-purple-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
            </div>
        );
    }

    // 미로그인: 로그인 화면
    if (!session) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-[#0f0c29] via-[#1a1a2e] to-[#1c1c3c] text-gray-200">
                <LoginScreen onGoogle={signInWithGoogle} />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-[#0f0c29] via-[#1a1a2e] to-[#1c1c3c] text-gray-200">
            {/* 우상단 로그아웃 버튼 */}
            <button
                type="button"
                onClick={signOut}
                title="로그아웃"
                className="fixed top-4 right-4 z-50 flex items-center gap-1.5 bg-gray-800/70 hover:bg-gray-700 border border-gray-700 text-gray-300 hover:text-white text-sm px-3 py-2 rounded-lg backdrop-blur-sm transition"
            >
                <ArrowLeftOnRectangleIcon className="w-4 h-4" />
                로그아웃
            </button>
            {roadmap ? (
                <Dashboard
                    roadmap={roadmap}
                    setRoadmap={setRoadmap}
                    messages={messages}
                    setMessages={setMessages}
                    onReset={handleReset}
                />
            ) : (
                <SetupScreen
                    onCreateRoadmap={handleCreateRoadmap}
                    roadmapList={roadmapList}
                    onLoadRoadmap={handleLoadRoadmap}
                    isLoading={isLoading}
                    error={error}
                />
            )}
        </div>
    );
};

export default App;