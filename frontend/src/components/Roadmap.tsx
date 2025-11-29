
import React from 'react';
import { Roadmap as RoadmapType, Curriculum, Mission } from '../types.ts';
import { CheckCircleIcon, CircleIcon } from './Icons.tsx';

interface RoadmapProps {
    roadmap: RoadmapType;
    onMissionToggle: (weekIndex: number, missionIndex: number) => void;
}

const Roadmap: React.FC<RoadmapProps> = ({ roadmap, onMissionToggle }) => {
    const totalMissions = roadmap.curriculum.reduce((acc, week) => acc + week.missions.length, 0);
    const completedMissions = roadmap.curriculum.reduce((acc, week) => acc + week.missions.filter(m => m.is_completed).length, 0);
    const progress = totalMissions > 0 ? (completedMissions / totalMissions) * 100 : 0;

    return (
        <div className="space-y-6">
            <div>
                <div className="flex justify-between items-center mb-2">
                    <h3 className="text-lg font-semibold text-gray-300">전체 진행률</h3>
                    <span className="text-sm font-medium text-purple-400">{Math.round(progress)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                    <div
                        className="bg-purple-500 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>
            </div>

            {roadmap.curriculum.map((week, weekIndex) => (
                <div key={week.week} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700/80">
                    <h4 className="text-lg font-bold text-white mb-3">{week.week}주차: <span className="font-normal">{week.theme}</span></h4>
                    <ul className="space-y-2">
                        {week.missions.map((mission, missionIndex) => (
                            <li key={mission.id}>
                                <label
                                    className={`flex items-center p-3 rounded-md transition-colors cursor-pointer ${
                                        mission.is_completed ? 'bg-green-900/30 text-gray-400' : 'bg-gray-700/50 hover:bg-gray-700'
                                    }`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={mission.is_completed}
                                        onChange={() => onMissionToggle(weekIndex, missionIndex)}
                                        className="hidden"
                                    />
                                    {mission.is_completed ? (
                                        <CheckCircleIcon className="w-6 h-6 text-green-400 mr-3 flex-shrink-0" />
                                    ) : (
                                        <CircleIcon className="w-6 h-6 text-gray-500 mr-3 flex-shrink-0" />
                                    )}
                                    <span className={`flex-grow ${mission.is_completed ? 'line-through' : ''}`}>
                                        {mission.title}
                                    </span>
                                </label>
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
};

export default Roadmap;
