
import React, { useState } from 'react';
import { Roadmap as RoadmapType, ChatMessage } from '../types.ts';
import Roadmap from './Roadmap.tsx';
import Chat from './Chat.tsx';
import { RobotIcon, ArrowLeftOnRectangleIcon } from './Icons.tsx';
import { completeMission } from '../hooks/useGemini.ts';

interface DashboardProps {
    roadmap: RoadmapType;
    setRoadmap: React.Dispatch<React.SetStateAction<RoadmapType | null>>;
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    onReset: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ roadmap, setRoadmap, messages, setMessages, onReset }) => {
    const [canCheck, setCanCheck] = useState(false);
    const [autoSendTrigger, setAutoSendTrigger] = useState(false);

    const handleMissionToggle = async (weekIndex: number, missionIndex: number) => {
        const newRoadmap = { ...roadmap };
        const mission = newRoadmap.curriculum[weekIndex].missions[missionIndex];

        // 체크박스를 해제하는 경우 (이미 완료된 것을 취소) -> 언제든 가능
        if (mission.is_completed) {
            mission.is_completed = false;
            setRoadmap(newRoadmap);
            return;
        }

        // 체크박스를 체크하려는 경우 (미완료 -> 완료) -> 검증 필요
        if (!canCheck) {
            alert("아직 학습 단계를 완료하지 않았습니다.\nAI 코치와 대화하여 검증을 통과한 후 체크해주세요!");
            return;
        }

        // 검증 통과 후 체크 (UI 즉시 업데이트)
        mission.is_completed = true;
        setRoadmap(newRoadmap);
        setCanCheck(false); // 다시 잠금

        // 서버 상태 업데이트
        if (roadmap.id) {
            try {
                await completeMission(roadmap.id, mission.id);
            } catch (error) {
                console.error("Failed to update mission status on server:", error);
                alert("서버에 저장하는 중 오류가 발생했습니다. 네트워크를 확인해주세요.");
            }
        } else {
            console.error("Roadmap ID is missing.");
        }
        
        // 자동으로 다음 단계 진행 트리거
        setAutoSendTrigger(true);
        setTimeout(() => setAutoSendTrigger(false), 1000);
    };

    const handleMissionCompleteSignal = () => {
        setCanCheck(true);
        // 사용자에게 시각적 피드백 (선택 사항, 여기서는 간단히 로그만)
        console.log("Mission Complete Signal Received! Checkbox Unlocked.");
    };

    return (
        <div className="flex flex-col md:flex-row h-screen max-h-screen overflow-hidden">
            <aside className="w-full md:w-1/3 lg:w-2/5 xl:w-1/3 bg-gray-900/70 border-r border-gray-700/50 flex flex-col">
                <header className="p-4 border-b border-gray-700/50 flex items-center justify-between flex-shrink-0">
                    <div className="flex items-center min-w-0">
                        <RobotIcon className="w-8 h-8 text-purple-400 mr-3 flex-shrink-0" />
                        <h1 className="text-xl font-bold font-space-grotesk truncate" title={roadmap.project_title}>
                            {roadmap.project_title}
                        </h1>
                    </div>
                    <button
                        onClick={onReset}
                        className="p-2 rounded-md text-gray-400 hover:bg-gray-700 hover:text-white transition-colors flex-shrink-0"
                        aria-label="처음부터 시작"
                    >
                        <ArrowLeftOnRectangleIcon className="w-5 h-5" />
                    </button>
                </header>
                <div className="flex-grow overflow-y-auto p-4">
                    <Roadmap roadmap={roadmap} onMissionToggle={handleMissionToggle} />
                </div>
            </aside>
            <main className="w-full md:w-2/3 lg:w-3/5 xl:w-2/3 flex flex-col h-full">
                <Chat 
                    roadmap={roadmap} 
                    messages={messages}
                    setMessages={setMessages}
                    onMissionCompleteSignal={handleMissionCompleteSignal}
                    autoSendTrigger={autoSendTrigger}
                />
            </main>
        </div>
    );
};

export default Dashboard;
