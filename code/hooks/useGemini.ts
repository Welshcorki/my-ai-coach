
import { GoogleGenAI, Type, GenerateContentResponse, Modality } from '@google/genai';
import { Roadmap, ChatMessage } from '../types.ts';

const API_KEY = process.env.API_KEY;
if (!API_KEY) {
    throw new Error("API_KEY environment variable not set.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY, vertexai: true });

const roadmapSchema = {
    type: Type.OBJECT,
    properties: {
        project_title: {
            type: Type.STRING,
            description: "사용자의 학습 프로젝트를 위한 창의적이고 동기를 부여하는 제목."
        },
        curriculum: {
            type: Type.ARRAY,
            description: "학습 계획의 주간별 분석.",
            items: {
                type: Type.OBJECT,
                properties: {
                    week: {
                        type: Type.INTEGER,
                        description: "주차 번호, 1부터 시작."
                    },
                    theme: {
                        type: Type.STRING,
                        description: "해당 주차의 주요 테마 또는 초점."
                    },
                    missions: {
                        type: Type.ARRAY,
                        description: "해당 주차의 구체적이고 실행 가능한 과제 또는 미션 목록.",
                        items: {
                            type: Type.OBJECT,
                            properties: {
                                id: {
                                    type: Type.STRING,
                                    description: "미션의 고유 식별자, 예: 'w1_m1'."
                                },
                                title: {
                                    type: Type.STRING,
                                    description: "미션의 명확하고 간결한 제목."
                                },
                                is_completed: {
                                    type: Type.BOOLEAN,
                                    description: "초기 완료 상태, 항상 false여야 함."
                                }
                            },
                            required: ["id", "title", "is_completed"]
                        }
                    }
                },
                required: ["week", "theme", "missions"]
            }
        }
    },
    required: ["project_title", "curriculum"]
};

export const generateRoadmap = async (goal: string, level: string, duration: number): Promise<Roadmap> => {
    const prompt = `당신은 'Grow'라는 이름의 전문 AI 커리큘럼 설계자입니다. 당신의 임무는 사용자를 위한 체계적인 주간 학습 로드맵을 만드는 것입니다. 출력은 제공된 스키마를 엄격히 준수하는 유효한 JSON 객체여야 합니다. 계획은 현실적이고 동기를 부여하며 실행 가능한 미션으로 나누어져야 합니다. 목표: "${goal}", 수준: "${level}", 기간: ${duration}주에 맞는 학습 계획을 만들어 주세요.`;

    try {
        const response: GenerateContentResponse = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: { role: 'user', parts: [{ text: prompt }] },
            config: {
                responseMimeType: 'application/json',
                responseSchema: roadmapSchema,
            },
        });

        const jsonString = response.text.trim();
        const parsedRoadmap = JSON.parse(jsonString);
        
        // Ensure is_completed is always false initially
        parsedRoadmap.curriculum.forEach((week: any) => {
            week.missions.forEach((mission: any) => {
                mission.is_completed = false;
            });
        });

        return parsedRoadmap as Roadmap;

    } catch (error) {
        console.error("Error generating roadmap:", error);
        throw new Error("학습 로드맵 생성에 실패했습니다. AI 모델을 일시적으로 사용할 수 없을 수 있습니다.");
    }
};

export const getChatResponseStream = async (history: ChatMessage[], currentContext: string) => {
    const model = 'gemini-2.5-flash';
    const chat = ai.chats.create({
        model: model,
        config: {
            systemInstruction: `당신은 'Grow'라는 이름의 친절하고 격려하는 AI 학습 코치입니다. 사용자는 학습 계획을 따르고 있습니다. 당신의 답변은 상황을 인지하고, 지지하며, 도움이 되어야 합니다. 답변은 간결하고 사용자의 현재 미션을 돕는 데 초점을 맞춰주세요. 현재 컨텍스트: ${currentContext}`,
        },
    });

    const lastUserMessage = history[history.length - 1];
    if (!lastUserMessage || lastUserMessage.role !== 'user') {
        throw new Error("Invalid chat history: last message must be from user.");
    }

    return await chat.sendMessageStream({ message: lastUserMessage.text });
};

export const reviewImage = async (base64Image: string, mimeType: string, prompt: string) => {
    const imagePart = {
        inlineData: {
            data: base64Image,
            mimeType: mimeType,
        },
    };

    const textPart = {
        text: `당신은 'Grow'라는 AI 학습 코치입니다. 사용자가 자신의 작업 증명으로 이미지를 제출했습니다. 이미지를 분석하고 사용자의 프롬프트에 기반하여 건설적이고 격려적인 피드백을 제공하세요. 사용자 프롬프트: "${prompt}". 잘한 점을 지적하고 개선할 점 한두 가지를 제안하세요. 이미지가 불분명하거나 관련이 없는 경우, 정중하게 더 나은 이미지를 요청하세요. 모델은 텍스트와 이미지 파트를 모두 출력할 수 있습니다.`,
    };

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash-image-preview',
            contents: {
                role: 'user',
                parts: [imagePart, textPart],
            },
            config: {
                responseModalities: [Modality.IMAGE, Modality.TEXT],
            },
        });
        
        let textResponse = "";
        let imageResponse: string | undefined = undefined;

        for (const part of response.candidates[0].content.parts) {
            if (part.text) {
                textResponse += part.text;
            } else if (part.inlineData) {
                imageResponse = `data:${part.inlineData.mimeType};base64,${part.inlineData.data}`;
            }
        }
        
        if (!textResponse && !imageResponse) {
            return { text: "죄송합니다, 이미지를 분석할 수 없습니다. 다시 시도해 주세요.", modelImage: undefined };
        }

        return { text: textResponse, modelImage: imageResponse };

    } catch (error) {
        console.error("Error reviewing image:", error);
        throw new Error("이미지 리뷰에 실패했습니다. Vision 모델을 일시적으로 사용할 수 없을 수 있습니다.");
    }
};
