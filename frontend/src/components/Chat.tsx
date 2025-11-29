import React, { useState, useRef, useEffect } from 'react';
import { Roadmap, ChatMessage } from '../types.ts';
import { getChatResponse, reviewImage } from '../hooks/useGemini.ts';
import { PaperAirplaneIcon, PaperClipIcon, XMarkIcon, SparklesIcon } from './Icons.tsx';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatProps {
    roadmap: Roadmap;
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    onMissionCompleteSignal: () => void;
    autoSendTrigger: boolean;
}

const Chat: React.FC<ChatProps> = ({ roadmap, messages, setMessages, onMissionCompleteSignal, autoSendTrigger }) => {
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // 자동 진행 트리거 감지
    useEffect(() => {
        if (autoSendTrigger) {
            const autoMessage = "체크 완료했습니다. 다음 단계로 진행해 주세요.";
            // 약간의 지연을 두어 자연스럽게 처리
            setTimeout(() => {
                handleAutoSend(autoMessage);
            }, 500);
        }
    }, [autoSendTrigger]);

    const handleAutoSend = async (text: string) => {
        if (!roadmap.id) {
            console.error("Roadmap ID missing for chat.");
            return;
        }
        setIsLoading(true);
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            text: text,
        };
        setMessages(prev => [...prev, userMessage]);

        const modelMessageId = (Date.now() + 1).toString();
        setMessages(prev => [...prev, { id: modelMessageId, role: 'model', text: '' }]);

        try {
            const currentWeek = roadmap.curriculum.find(w => w.missions.some(m => !m.is_completed)) || roadmap.curriculum[roadmap.curriculum.length - 1];
            const currentMission = currentWeek?.missions.find(m => !m.is_completed) || currentWeek?.missions[0];
            const context = `사용자는 ${currentWeek?.week}주차, 미션: "${currentMission?.title}"를 진행 중입니다.`;
            
            const modelResponse = await getChatResponse([...messages, userMessage], context, roadmap.id);
            
            let responseText = modelResponse.text;
            if (responseText.includes('[MISSION_COMPLETE]')) {
                onMissionCompleteSignal();
                responseText = responseText.replace('[MISSION_COMPLETE]', '').trim();
            }

            setMessages(prev => prev.map(msg => 
                msg.id === modelMessageId 
                ? { ...msg, text: responseText, role: modelResponse.role } 
                : msg
            ));
        } catch (error) {
            console.error(error);
            const errorText = error instanceof Error ? error.message : "죄송합니다, 오류가 발생했습니다.";
            setMessages(prev => prev.map(msg => msg.id === modelMessageId ? { ...msg, text: `오류: ${errorText}` } : msg));
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // AI 응답 완료 후 입력창에 포커스
    useEffect(() => {
        if (!isLoading) {
            setTimeout(() => {
                textareaRef.current?.focus();
            }, 50);
        }
    }, [isLoading]);

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setImageFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const removeImage = () => {
        setImageFile(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const fileToBase64 = (file: File): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve((reader.result as string).split(',')[1]);
            reader.onerror = error => reject(error);
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() && !imageFile) return;

        if (!roadmap.id) {
            console.error("Roadmap ID missing for chat.");
            alert("로드맵 ID 오류입니다. 새로고침 해주세요.");
            return;
        }

        setIsLoading(true);
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            text: input,
            image: imagePreview || undefined,
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setImageFile(null);
        setImagePreview(null);

        const modelMessageId = (Date.now() + 1).toString();
        setMessages(prev => [...prev, { id: modelMessageId, role: 'model', text: '' }]);

        try {
            if (imageFile) {
                const base64Image = await fileToBase64(imageFile);
                const result = await reviewImage(base64Image, imageFile.type, input);
                setMessages(prev => prev.map(msg => msg.id === modelMessageId ? { ...msg, text: result.text, modelImage: result.modelImage } : msg));
            } else {
                const currentWeek = roadmap.curriculum.find(w => w.missions.some(m => !m.is_completed)) || roadmap.curriculum[roadmap.curriculum.length - 1];
                const currentMission = currentWeek?.missions.find(m => !m.is_completed) || currentWeek?.missions[0];
                const context = `사용자는 ${currentWeek?.week}주차, 미션: "${currentMission?.title}"를 진행 중입니다.`;
                
                const modelResponse = await getChatResponse([...messages, userMessage], context, roadmap.id);
                
                let responseText = modelResponse.text;
                if (responseText.includes('[MISSION_COMPLETE]')) {
                    onMissionCompleteSignal();
                    responseText = responseText.replace('[MISSION_COMPLETE]', '').trim();
                }

                // 기존 메시지 ID를 사용하여 전체 메시지 객체로 상태를 업데이트합니다.
                setMessages(prev => prev.map(msg => 
                    msg.id === modelMessageId 
                    ? { ...msg, text: responseText, role: modelResponse.role } 
                    : msg
                ));
            }
        } catch (error) {
            console.error(error);
            const errorText = error instanceof Error ? error.message : "죄송합니다, 오류가 발생했습니다.";
            setMessages(prev => prev.map(msg => msg.id === modelMessageId ? { ...msg, text: `오류: ${errorText}` } : msg));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-800/50">
            <div className="flex-grow p-4 overflow-y-auto">
                <div className="space-y-6 max-w-4xl mx-auto">
                    {messages.map((msg) => {
                        // 빈 메시지(로딩 중인 상태)는 렌더링하지 않음 (별도 로딩 UI가 처리)
                        if (msg.role === 'model' && !msg.text && !msg.modelImage) return null;
                        
                        return (
                            <div key={msg.id} className={`flex items-end gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                {msg.role === 'model' && <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0"><SparklesIcon className="w-5 h-5 text-white"/></div>}
                                <div className={`max-w-xl p-4 rounded-2xl ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-lg' : 'bg-gray-700 text-gray-200 rounded-bl-lg'}`}>
                                    {msg.image && <img src={msg.image} alt="사용자 업로드" className="rounded-lg mb-2 max-h-60" />}
                                    <div className="prose prose-invert prose-sm max-w-none">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                                    </div>
                                    {msg.modelImage && <img src={msg.modelImage} alt="모델 생성 이미지" className="rounded-lg mt-2 max-h-60" />}
                                </div>
                            </div>
                        );
                    })}
                    {isLoading && messages[messages.length - 1]?.role === 'model' && (
                         <div className="flex items-end gap-3 justify-start">
                            <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0"><SparklesIcon className="w-5 h-5 text-white"/></div>
                            <div className="max-w-xl p-4 rounded-2xl bg-gray-700 text-gray-200 rounded-bl-lg">
                                <div className="flex items-center space-x-2">
                                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>
            <div className="p-4 border-t border-gray-700/50 bg-gray-800/80">
                <div className="max-w-4xl mx-auto">
                    {imagePreview && (
                        <div className="relative inline-block mb-2">
                            <img src={imagePreview} alt="미리보기" className="h-24 w-auto rounded-lg" />
                            <button onClick={removeImage} className="absolute -top-2 -right-2 bg-gray-900 rounded-full p-1 text-white hover:bg-red-500">
                                <XMarkIcon className="w-4 h-4" />
                            </button>
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="flex items-center gap-2 bg-gray-900 border border-gray-600 rounded-xl p-2">
                        <button type="button" onClick={() => fileInputRef.current?.click()} className="p-2 text-gray-400 hover:text-purple-400 rounded-full hover:bg-gray-700 transition-colors">
                            <PaperClipIcon className="w-6 h-6" />
                        </button>
                        <input type="file" accept="image/*" ref={fileInputRef} onChange={handleImageChange} className="hidden" />
                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSubmit(e);
                                }
                            }}
                            placeholder="피드백을 요청하거나 학습 증거를 업로드하세요..."
                            className="flex-grow bg-transparent text-white placeholder-gray-500 focus:outline-none resize-none max-h-32"
                            rows={1}
                            disabled={isLoading}
                        />
                        <button type="submit" disabled={isLoading || (!input.trim() && !imageFile)} className="p-2 rounded-full bg-purple-600 text-white disabled:bg-purple-800 disabled:cursor-not-allowed hover:bg-purple-700 transition-colors">
                            <PaperAirplaneIcon className="w-6 h-6" />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Chat;