
import React, { useState } from 'react';
import { Roadmap as RoadmapType } from '../types.ts';
import Roadmap from './Roadmap.tsx';
import Chat from './Chat.tsx';
import { RobotIcon, ArrowLeftOnRectangleIcon } from './Icons.tsx';

interface DashboardProps {
    roadmap: RoadmapType;
    setRoadmap: React.Dispatch<React.SetStateAction<RoadmapType | null>>;
    onReset: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ roadmap, setRoadmap, onReset }) => {
    const handleMissionToggle = (weekIndex: number, missionIndex: number) => {
        const newRoadmap = { ...roadmap };
        const mission = newRoadmap.curriculum[weekIndex].missions[missionIndex];
        mission.is_completed = !mission.is_completed;
        setRoadmap(newRoadmap);
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
                <Chat roadmap={roadmap} />
            </main>
        </div>
    );
};

export default Dashboard;
