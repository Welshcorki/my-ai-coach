
import React, { useState, useCallback } from 'react';
import { Roadmap } from './types.ts';
import SetupScreen from './components/SetupScreen.tsx';
import Dashboard from './components/Dashboard.tsx';
import { generateRoadmap } from './hooks/useGemini.ts';

const App: React.FC = () => {
    const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const handleCreateRoadmap = useCallback(async (goal: string, level: string, duration: number) => {
        setIsLoading(true);
        setError(null);
        try {
            const newRoadmap = await generateRoadmap(goal, level, duration);
            setRoadmap(newRoadmap);
        } catch (err) {
            console.error(err);
            setError(err instanceof Error ? err.message : '로드맵을 생성하는 중 알 수 없는 오류가 발생했습니다.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const handleReset = () => {
        setRoadmap(null);
        setError(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-[#0f0c29] via-[#1a1a2e] to-[#1c1c3c] text-gray-200">
            {roadmap ? (
                <Dashboard roadmap={roadmap} setRoadmap={setRoadmap} onReset={handleReset} />
            ) : (
                <SetupScreen
                    onCreateRoadmap={handleCreateRoadmap}
                    isLoading={isLoading}
                    error={error}
                />
            )}
        </div>
    );
};

export default App;
