
import { Roadmap, ChatMessage } from '../types.ts';

// FastAPI 백엔드 서버의 주소
const BASE_URL = 'http://127.0.0.1:8000/api/v1';

/**
 * API 요청을 위한 헬퍼 함수
 * @param endpoint API 엔드포인트 경로
 * @param options fetch 요청 옵션
 * @returns Promise<T>
 */
async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: response.statusText }));
            throw new Error(errorData.detail || errorData.message || 'API 요청에 실패했습니다.');
        }
        return await response.json();
    } catch (error) {
        console.error(`API Error at ${endpoint}:`, error);
        if (error instanceof Error) {
            throw new Error(`네트워크 오류 또는 서버에 연결할 수 없습니다: ${error.message}`);
        }
        throw new Error('알 수 없는 네트워크 오류가 발생했습니다.');
    }
}

export const generateRoadmap = async (goal: string, level: string, duration: number): Promise<Roadmap> => {
    return fetchAPI<Roadmap>('/plan', {
        method: 'POST',
        body: JSON.stringify({ goal, level, duration }),
    });
};

// 참고: 스트리밍을 지원하려면 이 함수와 Chat.tsx의 로직 수정이 필요합니다.
// 우선 통합을 위해 간단한 요청/응답 모델로 변경합니다.
export const getChatResponse = async (history: ChatMessage[], currentContext: string): Promise<ChatMessage> => {
    const lastUserMessage = history[history.length - 1];
    if (!lastUserMessage || lastUserMessage.role !== 'user') {
        throw new Error("Invalid chat history: last message must be from user.");
    }

    return fetchAPI<ChatMessage>('/chat', {
        method: 'POST',
        body: JSON.stringify({
            history: history,
            context: currentContext,
            message: lastUserMessage.text,
        }),
    });
};

export const reviewImage = async (base64Image: string, mimeType: string, prompt: string): Promise<{ text: string; modelImage?: string }> => {
    return fetchAPI<{ text: string; modelImage?: string }>('/review', {
        method: 'POST',
        body: JSON.stringify({ base64Image, mimeType, prompt }),
    });
};
