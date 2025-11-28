
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
    project_title: string;
    curriculum: Curriculum[];
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'model';
    text: string;
    image?: string; // base64 data URL for display
    modelImage?: string; // base64 data URL from model
}
