
export interface Mission {
    id: string;
    title: string;
    is_completed: boolean;
}

export interface Curriculum {
    week: number;
    theme: string;
    missions: Mission[];
}

export interface Roadmap {
    id?: number;
    project_title: string;
    curriculum: Curriculum[];
}

export interface RoadmapWithHistory extends Roadmap {
    id: number;
    chat_history: ChatMessage[];
}

export interface RoadmapSummary {
    id: number;
    project_title: string;
    goal: string;
    level: string;
    created_at: string;
    total_missions: number;
    completed_missions: number;
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'model';
    text: string;
    image?: string; // base64 data URL for display
    modelImage?: string; // base64 data URL from model
}
