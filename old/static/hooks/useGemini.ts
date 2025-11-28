import { Roadmap, ChatMessage } from '../types.ts';

// Helper function to handle API errors
const handleApiError = (error: any, defaultMessage: string): Error => {
    console.error("API Error:", error);
    if (error instanceof Error) {
        return error;
    }
    return new Error(defaultMessage);
};

export const generateRoadmap = async (goal: string, level: string, duration: number): Promise<Roadmap> => {
    try {
        const response = await fetch('/api/v1/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ goal, level, duration }), // Sending all params
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // The backend's planner_node returns a stringified JSON inside the 'plan' key.
        // We need to parse it.
        const parsedRoadmap = JSON.parse(data.plan);

        // Ensure is_completed is always false initially, just in case
        if (parsedRoadmap.curriculum) {
            parsedRoadmap.curriculum.forEach((week: any) => {
                if (week.missions) {
                    week.missions.forEach((mission: any) => {
                        mission.is_completed = false;
                    });
                }
            });
        }

        return parsedRoadmap as Roadmap;

    } catch (error) {
        throw handleApiError(error, "학습 로드맵 생성에 실패했습니다. 백엔드 서버에 문제가 있을 수 있습니다.");
    }
};

// This function is now async, not a stream generator.
export const getChatResponse = async (history: ChatMessage[], currentContext: string): Promise<string> => {
    const lastUserMessage = history[history.length - 1];
    if (!lastUserMessage || lastUserMessage.role !== 'user') {
        throw new Error("Invalid chat history: last message must be from user.");
    }

    try {
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: lastUserMessage.text, sender: 'user', context: currentContext }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.content;

    } catch (error) {
        throw handleApiError(error, "채팅 응답을 가져오는 데 실패했습니다.");
    }
};


export const reviewImage = async (base64Image: string, mimeType: string, prompt: string): Promise<{ text: string, modelImage?: string }> => {
    try {
        const response = await fetch('/api/v1/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ base64_image: base64Image, mime_type: mimeType, prompt }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        // The backend returns { feedback: string }. Adapt to the expected return type.
        return { text: data.feedback };

    } catch (error) {
        throw handleApiError(error, "이미지 리뷰에 실패했습니다. 백엔드 서버에 문제가 있을 수 있습니다.");
    }
};