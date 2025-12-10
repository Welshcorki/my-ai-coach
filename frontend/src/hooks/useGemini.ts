
import { Roadmap, ChatMessage, RoadmapWithHistory, RoadmapSummary } from '../types.ts';

// FastAPI 백엔드 서버의 주소
// 배포 환경에서는 같은 도메인에서 서빙되므로 상대 경로 사용
// 로컬 개발 환경에서는 Vite 프록시 설정을 사용하거나 환경 변수로 설정 가능
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

/**
 * API 요청을 위한 헬퍼 함수
 * @param endpoint API 엔드포인트 경로
 * @param options fetch 요청 옵션
 * @returns Promise<T>
 */
async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
        const headers: HeadersInit = {
            ...options.headers,
        };

        // FormData가 아닐 때만 Content-Type: application/json 추가
        if (!(options.body instanceof FormData)) {
            (headers as Record<string, string>)['Content-Type'] = 'application/json';
        }

        const response = await fetch(`${BASE_URL}${endpoint}`, {
            ...options,
            headers,
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

export const generateRoadmap = async (goal: string, level: string, duration: number, frequency: string, file?: File | null): Promise<Roadmap> => {
    const formData = new FormData();
    formData.append('goal', goal);
    formData.append('level', level);
    formData.append('duration', duration.toString());
    formData.append('frequency', frequency);
    
    if (file) {
        formData.append('file', file);
    }

    return fetchAPI<Roadmap>('/plan', {
        method: 'POST',
        body: formData,
    });
};

export const getAllRoadmaps = async (): Promise<RoadmapSummary[]> => {
    return fetchAPI<RoadmapSummary[]>('/roadmaps', { method: 'GET' });
};

export const getRoadmapDetail = async (id: number): Promise<RoadmapWithHistory> => {
    return fetchAPI<RoadmapWithHistory>(`/roadmap/${id}`, { method: 'GET' });
};

export const completeMission = async (roadmapId: number, missionKey: string): Promise<{ status: string, roadmap_id: number, mission_key: string }> => {
    return fetchAPI<{ status: string, roadmap_id: number, mission_key: string }>(`/roadmap/${roadmapId}/mission/${missionKey}/complete`, {
        method: 'PUT',
    });
};

// 참고: 스트리밍을 지원하려면 이 함수와 Chat.tsx의 로직 수정이 필요합니다.
// 우선 통합을 위해 간단한 요청/응답 모델로 변경합니다.
export const getChatResponse = async (history: ChatMessage[], currentContext: string, roadmapId: number): Promise<ChatMessage> => {
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
            roadmap_id: roadmapId
        }),
    });
};

export const reviewImage = async (base64Image: string, mimeType: string, prompt: string): Promise<{ text: string; modelImage?: string }> => {
    return fetchAPI<{ text: string; modelImage?: string }>('/review', {
        method: 'POST',
        body: JSON.stringify({ base64Image, mimeType, prompt }),
    });
};
