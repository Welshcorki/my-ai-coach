import React from 'react';
import { RobotIcon } from './Icons.tsx';

interface LoginScreenProps {
    onGoogle: () => void;
}

// Google 브랜드 G 로고 (멀티컬러)
const GoogleLogo: React.FC<{ className?: string }> = ({ className }) => (
    <svg className={className} viewBox="0 0 48 48" aria-hidden="true">
        <path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"/>
        <path fill="#FF3D00" d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"/>
        <path fill="#4CAF50" d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"/>
        <path fill="#1976D2" d="M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571.001-.001.002-.001.003-.002l6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z"/>
    </svg>
);

const LoginScreen: React.FC<LoginScreenProps> = ({ onGoogle }) => {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4">
            <div className="w-full max-w-md bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 shadow-2xl shadow-purple-900/20">
                <div className="text-center mb-8">
                    <div className="inline-block bg-purple-500/10 p-4 rounded-full mb-4">
                        <RobotIcon className="w-12 h-12 text-purple-400" />
                    </div>
                    <h1 className="text-3xl font-bold font-space-grotesk text-white">AI 자기 계발 코치</h1>
                    <p className="text-gray-400 mt-2">로그인하고 나만의 학습 로드맵을 시작하세요.</p>
                </div>

                {/* 소셜 로그인 영역 (추후 이메일+비밀번호 폼을 이 아래에 추가) */}
                <div className="space-y-4">
                    <button
                        type="button"
                        onClick={onGoogle}
                        className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-100 text-gray-800 font-semibold py-3 px-4 rounded-lg transition-all duration-300 transform hover:scale-105"
                    >
                        <GoogleLogo className="w-5 h-5" />
                        Google로 계속하기
                    </button>
                </div>

                <p className="text-xs text-gray-500 text-center mt-8">
                    로그인 시 학습 기록이 계정에 안전하게 저장됩니다.
                </p>
            </div>
        </div>
    );
};

export default LoginScreen;
