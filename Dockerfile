# [Stage 1] Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# 패키지 파일 복사
COPY frontend/package*.json ./

# npm install (package-lock.json이 없어도 작동)
RUN npm install

# 소스 복사 및 빌드
COPY frontend/ .
RUN npm run build

# 빌드 결과물 확인: vite.config.ts에서 outDir: '../static'로 설정되어 있으므로
# /app/frontend에서 빌드하면 /app/static에 생성됨

# [Stage 2] Backend Runtime
FROM python:3.11-slim
WORKDIR /app

# 타임존 설정 (선택사항: 로그 시간 확인용)
ENV TZ=Asia/Seoul

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프론트엔드 빌드 결과물 복사
# vite.config.ts에서 outDir: '../static'로 설정되어 있으므로
# /app/frontend에서 빌드 시 /app/static에 생성됨
COPY --from=frontend-builder /app/static ./static

# 백엔드 코드 복사
COPY app/ ./app/
COPY main.py .

# 포트 설정 (Cloud Run 기본값 8080, 환경 변수로 오버라이드 가능)
ENV PORT=8080
EXPOSE 8080

# [개선된 실행 명령어]
# uvicorn을 직접 실행하여 환경 변수($PORT)를 확실하게 반영
# main.py를 거치지 않고 직접 실행하는 것이 더 명확하고 성능상 유리
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}

