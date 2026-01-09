import React, { useState, useEffect } from 'react';
import { RobotIcon, SparklesIcon } from './Icons.tsx';
import { RoadmapSummary } from '../types.ts';
import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';
import { getHeatmapData } from '../hooks/useGemini.ts';

interface SetupScreenProps {
    onCreateRoadmap: (goal: string, level: string, duration: number, frequency: string, file: File | null) => void;
    roadmapList: RoadmapSummary[];
    onLoadRoadmap: (id: number) => void;
    isLoading: boolean;
    error: string | null;
}

const SetupScreen: React.FC<SetupScreenProps> = ({ onCreateRoadmap, roadmapList, onLoadRoadmap, isLoading, error }) => {
    const [goal, setGoal] = useState('');
    const [level, setLevel] = useState('초급');
    const [duration, setDuration] = useState(4);
    const [frequency, setFrequency] = useState('매일 (월~금, 5일)');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [heatmapData, setHeatmapData] = useState<{ date: string, count: number }[]>([]);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getHeatmapData();
                setHeatmapData(data);
            } catch (err) {
                console.error("Failed to fetch stats:", err);
            }
        };
        fetchStats();
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            if (file.type === 'application/pdf') {
                setSelectedFile(file);
            } else {
                alert('PDF 파일만 업로드할 수 있습니다.');
            }
        }
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (goal.trim() && duration > 0) {
            onCreateRoadmap(goal, level, duration, frequency, selectedFile);
        }
    };

    const today = new Date();
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(today.getFullYear() - 1);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4 max-w-7xl mx-auto">
            <div className="text-center mb-8 mt-8">
                <div className="inline-block bg-purple-500/10 p-4 rounded-full mb-4">
                    <RobotIcon className="w-12 h-12 text-purple-400" />
                </div>
                <h1 className="text-4xl md:text-5xl font-bold font-space-grotesk text-white">AI 자기 계발 코치</h1>
                <p className="text-lg text-gray-400 mt-2">목표를 정의하세요. 숙련으로 가는 길을 함께 만들어가요.</p>
            </div>

            {/* 히트맵 섹션 (잔디 심기) */}
            <div className="w-full bg-gray-800/30 border border-gray-700/50 rounded-2xl p-6 mb-12 backdrop-blur-sm shadow-xl">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-bold text-gray-300 flex items-center">
                        <span className="mr-2">🌱</span> 나의 학습 열정 (최근 1년)
                    </h2>
                    <div className="text-xs text-gray-500 flex items-center gap-2">
                        Less <div className="flex gap-1"><div className="w-3 h-3 bg-gray-700 rounded-sm"></div><div className="w-3 h-3 bg-purple-900 rounded-sm"></div><div className="w-3 h-3 bg-purple-700 rounded-sm"></div><div className="w-3 h-3 bg-purple-500 rounded-sm"></div><div className="w-3 h-3 bg-purple-300 rounded-sm"></div></div> More
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <div className="min-w-[800px]">
                        <CalendarHeatmap
                            startDate={oneYearAgo}
                            endDate={today}
                            values={heatmapData}
                            classForValue={(value) => {
                                if (!value || value.count === 0) return 'color-empty';
                                if (value.count < 3) return 'color-scale-1';
                                if (value.count < 6) return 'color-scale-2';
                                if (value.count < 10) return 'color-scale-3';
                                return 'color-scale-4';
                            }}
                            // @ts-ignore
                            tooltipDataAttrs={(value: any) => {
                                if (!value || !value.date) return { 'data-tooltip-id': 'heatmap-tooltip', 'data-tooltip-content': '활동 없음' };
                                return {
                                    'data-tooltip-id': 'heatmap-tooltip',
                                    'data-tooltip-content': `${value.date}: ${value.count} 활동량`,
                                };
                            }}
                        />
                        <Tooltip id="heatmap-tooltip" />
                    </div>
                </div>
                <style>{`
                    .react-calendar-heatmap .color-empty { fill: #1f2937; }
                    .react-calendar-heatmap .color-scale-1 { fill: #4c1d95; }
                    .react-calendar-heatmap .color-scale-2 { fill: #6d28d9; }
                    .react-calendar-heatmap .color-scale-3 { fill: #8b5cf6; }
                    .react-calendar-heatmap .color-scale-4 { fill: #c084fc; }
                    .react-calendar-heatmap rect { rx: 2; ry: 2; }
                `}</style>
            </div>

            <div className="flex flex-col lg:flex-row gap-8 w-full items-start justify-center">
                {/* 왼쪽: 새 로드맵 생성 폼 */}
                <div className="w-full max-w-lg bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 shadow-2xl shadow-purple-900/20 flex-shrink-0">
                     <h2 className="text-xl font-bold text-white mb-6 flex items-center border-b border-gray-700 pb-2">
                        <SparklesIcon className="w-5 h-5 mr-2 text-purple-400"/>
                        새로운 학습 시작하기
                     </h2>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        
                        {/* 파일 업로드 UI */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-300 mb-2">학습 교재 (PDF, 선택사항)</label>
                            {!selectedFile ? (
                                <label className="flex flex-col items-center justify-center w-full h-24 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-900 hover:bg-gray-800 transition">
                                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                        <svg className="w-8 h-8 mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                                        <p className="text-xs text-gray-400">PDF 파일을 드래그하거나 클릭하여 업로드</p>
                                    </div>
                                    <input type="file" className="hidden" onChange={handleFileChange} accept=".pdf" />
                                </label>
                            ) : (
                                <div className="flex items-center justify-between p-3 bg-purple-900/30 border border-purple-500/50 rounded-lg">
                                    <div className="flex items-center space-x-3 overflow-hidden">
                                        <svg className="w-6 h-6 text-purple-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                        <span className="text-sm text-gray-200 truncate">{selectedFile.name}</span>
                                    </div>
                                    <button type="button" onClick={handleRemoveFile} className="text-gray-400 hover:text-white transition">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                                    </button>
                                </div>
                            )}
                        </div>

                        <div>
                            <label htmlFor="goal" className="block text-sm font-medium text-gray-300 mb-2">무엇을 마스터하고 싶으신가요?</label>
                            <input
                                type="text"
                                id="goal"
                                value={goal}
                                onChange={(e) => setGoal(e.target.value)}
                                placeholder="예: 'React와 TypeScript'"
                                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                                required
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label htmlFor="level" className="block text-sm font-medium text-gray-300 mb-2">현재 당신의 수준은?</label>
                                <select
                                    id="level"
                                    value={level}
                                    onChange={(e) => setLevel(e.target.value)}
                                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                                >
                                    <option>초급</option>
                                    <option>중급</option>
                                    <option>고급</option>
                                </select>
                            </div>
                            <div>
                                <label htmlFor="duration" className="block text-sm font-medium text-gray-300 mb-2">학습 기간 (주)</label>
                                <input
                                    type="number"
                                    id="duration"
                                    value={duration}
                                    min="1"
                                    max="52"
                                    onChange={(e) => setDuration(parseInt(e.target.value, 10))}
                                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                                    required
                                />
                            </div>
                            <div className="md:col-span-2">
                                <label htmlFor="frequency" className="block text-sm font-medium text-gray-300 mb-2">주당 학습 빈도</label>
                                <select
                                    id="frequency"
                                    value={frequency}
                                    onChange={(e) => setFrequency(e.target.value)}
                                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                                >
                                    <option>매일 (월~금, 5일)</option>
                                    <option>주 3일 (월/수/금)</option>
                                    <option>주 2일 (주말 집중)</option>
                                    <option>자유롭게 (주 3~4회)</option>
                                </select>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full flex items-center justify-center bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 transform hover:scale-105"
                        >
                            {isLoading ? (
                                <>
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    계획을 생성 중입니다...
                                </>
                            ) : (
                                <>
                                    <SparklesIcon className="w-5 h-5 mr-2" />
                                    내 로드맵 생성하기
                                </>
                            )}
                        </button>
                    </form>
                    {error && <p className="mt-4 text-center text-red-400 bg-red-900/50 p-3 rounded-lg">{error}</p>}
                </div>

                {/* 오른쪽: 나의 학습 목록 (목록이 있을 때만 표시) */}
                {roadmapList.length > 0 && (
                    <div className="w-full max-w-lg bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 shadow-2xl shadow-blue-900/20 flex-shrink-0 h-full max-h-[800px] flex flex-col">
                        <h2 className="text-xl font-bold text-white mb-6 flex items-center border-b border-gray-700 pb-2">
                            <span className="text-2xl mr-2">📚</span>
                            나의 학습 목록
                        </h2>
                        <div className="flex-grow overflow-y-auto space-y-4 pr-2">
                            {roadmapList.map(item => (
                                <div key={item.id} onClick={() => onLoadRoadmap(item.id)} className="bg-gray-700/50 hover:bg-gray-700 p-5 rounded-xl cursor-pointer transition-all border border-gray-600 hover:border-purple-500 group shadow-md">
                                    <h3 className="font-bold text-white text-lg group-hover:text-purple-400 transition-colors truncate">{item.project_title}</h3>
                                    <div className="text-sm text-gray-400 mt-2 flex justify-between">
                                        <span className="truncate max-w-[150px]">{item.goal}</span>
                                        <span className="text-gray-500 text-xs bg-gray-800 px-2 py-1 rounded">{item.level}</span>
                                    </div>
                                    <div className="mt-4 w-full bg-gray-800 rounded-full h-2">
                                        <div className="bg-green-500 h-2 rounded-full transition-all duration-500" style={{ width: `${item.total_missions > 0 ? (item.completed_missions / item.total_missions) * 100 : 0}%` }}></div>
                                    </div>
                                    <div className="flex justify-between items-center mt-2">
                                        <span className="text-xs text-gray-500">{new Date(item.created_at).toLocaleDateString()}</span>
                                        <span className="text-xs font-medium text-green-400">
                                            진행률: {item.total_missions > 0 ? Math.round((item.completed_missions / item.total_missions) * 100) : 0}%
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SetupScreen;