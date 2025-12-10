import React, { useState, useCallback, useEffect } from 'react';
import { Roadmap, ChatMessage, RoadmapSummary } from './types.ts';
import SetupScreen from './components/SetupScreen.tsx';
import Dashboard from './components/Dashboard.tsx';
import { generateRoadmap, getAllRoadmaps, getRoadmapDetail } from './hooks/useGemini.ts';

const App: React.FC = () => {
    const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [roadmapList, setRoadmapList] = useState<RoadmapSummary[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // 앱 시작 시 학습 목록 로드
    useEffect(() => {
        loadRoadmapList();
    }, []);

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

    return (
        <div className="min-h-screen bg-gradient-to-b from-[#0f0c29] via-[#1a1a2e] to-[#1c1c3c] text-gray-200">
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