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
| `FRONTEND_ORIGINS` | CORS 허용 origin, 콤마로 여러 개 지정 가능 (기본 `http://localhost:5173,https://logo-gen-ten.vercel.app`) | - |

## 환경 변수 (`frontend/.env`)

| 변수 | 설명 | 미설정 시 동작 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | 배포된 백엔드 주소 (예: `https://logo-gen-api.onrender.com`) | Vite dev 서버 프록시로 `localhost:8000` 사용 (로컬 개발용) |

## 배포 (프론트/백엔드 분리 배포)

프론트엔드(Vercel 등 정적 호스팅)와 백엔드(FastAPI)는 서로 다른 도메인에
배포되므로, 로컬 개발 때 쓰던 Vite 프록시(`/api` → `localhost:8000`)는
배포본에는 적용되지 않습니다. 아래 순서로 배포하세요.

### 1. 백엔드를 Render에 배포

1. https://render.com 가입 후 **New → Web Service** 선택, 이 GitHub 저장소 연결
   (저장소 루트에 있는 `render.yaml`을 인식하면 **New → Blueprint**로도 자동 설정 가능)
2. 수동으로 만들 경우 다음 값을 입력:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Environment 탭에서 환경 변수 등록: `OPENAI_API_KEY`, `HF_TOKEN` (Secret),
   `OPENAI_MODEL`, `HF_T2I_MODEL`, `FRONTEND_ORIGINS`(실제 프론트 배포 주소 포함)
4. 배포 완료 후 발급되는 주소(예: `https://logo-gen-api.onrender.com`)를 기록

### 2. 프론트엔드(Vercel)에 백엔드 주소 연결

1. Vercel 프로젝트 → **Settings → Environment Variables**에서
   `VITE_API_BASE_URL` = 1번에서 발급받은 Render 백엔드 주소로 등록
   (Root Directory는 `frontend`로 설정되어 있어야 합니다)
2. 저장 후 **Redeploy** 실행

### 3. 확인

배포된 프론트엔드 주소로 접속해 회사명/슬로건 입력 → "프롬프트 생성" →
"최종 로고 생성"까지 정상 동작하는지 확인. 만약 CORS 에러가 뜨면 백엔드의
`FRONTEND_ORIGINS`에 프론트엔드 배포 주소가 정확히 포함되어 있는지 확인하세요.

## API

- `POST /api/prompt/generate` — `{ company_name, slogan, industry?, style?, colors? }`
  → `{ thread_id, generated_prompt, prompt_source, steps }`
- `POST /api/logo/generate` — `{ thread_id }`
  → `{ images, image_source, steps }` (images는 base64 PNG data URL 3개)
- `GET /api/health` — 서버 상태 및 실제 API 연동 여부 확인
