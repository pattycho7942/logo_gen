# LogoGen AI

기업명과 슬로건(+업종/스타일/색상)을 입력하면 AI가 로고 시안 3개를 자동으로
생성해주는 웹 서비스입니다. LangGraph로 파이프라인을 구성해 진행 단계를
단계별로 시각화하고, ChatGPT(LLM)로 이미지 생성 프롬프트를 보강한 뒤
HuggingFace text-to-image 모델로 로고 이미지를 생성합니다.

학습 진행 순서: **AI → LLM → EDA → ChatGPT+HuggingFace → LangChain/LangGraph**

## 아키텍처

- **백엔드**: FastAPI + LangGraph (`backend/`)
  - `app/graph.py` — 3단계 노드(`collect_input` → `generate_prompt` →
    `generate_logos`)로 구성된 StateGraph. `MemorySaver` 체크포인터와
    `interrupt_after`를 사용해 "프롬프트 생성" 버튼과 "최종 로고 생성" 버튼,
    두 번의 API 호출에 걸쳐 하나의 그래프 실행을 이어갑니다.
  - `app/services/llm_service.py` — OpenAI(ChatGPT) API로 프롬프트 보강,
    키가 없으면 템플릿 조합으로 자동 대체(fallback).
  - `app/services/image_service.py` — HuggingFace Inference API
    (`text_to_image`)로 로고 3장 생성, 키가 없으면 Pillow로 만든 데모용
    플레이스홀더 로고 3종으로 자동 대체.
- **프론트엔드**: React + Vite + TypeScript + Tailwind CSS (`frontend/`)
  - 4단계 진행 스테퍼(`StepProgress`), 입력 폼(`LogoForm`), 프롬프트
    미리보기(`PromptPreview`), 결과 그리드(`ResultsGrid`)로 구성.

API 키가 없어도 전체 플로우가 데모(mock) 모드로 동작하며, `.env`에 실제 키를
넣으면 자동으로 실제 API 호출로 전환됩니다.

## 실행 방법

### 백엔드

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 필요시 OPENAI_API_KEY / HF_TOKEN 입력
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173` 접속. `/api/*` 요청은 Vite dev 서버
프록시를 통해 백엔드(`:8000`)로 전달됩니다.

## 환경 변수 (`backend/.env`)

| 변수 | 설명 | 미설정 시 동작 |
| --- | --- | --- |
| `OPENAI_API_KEY` | ChatGPT 프롬프트 보강용 | 템플릿 조합으로 프롬프트 생성 |
| `OPENAI_MODEL` | 사용할 OpenAI 모델 (기본 `gpt-4o-mini`) | - |
| `HF_TOKEN` | HuggingFace Inference API 토큰 | Pillow 플레이스홀더 로고 3종 생성 |
| `HF_T2I_MODEL` | text-to-image 모델 (기본 `black-forest-labs/FLUX.1-schnell`) | - |
| `FRONTEND_ORIGIN` | CORS 허용 origin (기본 `http://localhost:5173`) | - |

## API

- `POST /api/prompt/generate` — `{ company_name, slogan, industry?, style?, colors? }`
  → `{ thread_id, generated_prompt, prompt_source, steps }`
- `POST /api/logo/generate` — `{ thread_id }`
  → `{ images, image_source, steps }` (images는 base64 PNG data URL 3개)
- `GET /api/health` — 서버 상태 및 실제 API 연동 여부 확인
