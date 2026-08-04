# LogoGen AI

기업명과 슬로건(+업종/스타일/색상)을 입력하면 AI가 로고 시안 3개를 한 번에
자동으로 생성해주고, 마음에 드는 시안을 클릭하는 즉시 그 로고로 명함까지
만들어주는 웹 서비스입니다. LangGraph로 파이프라인을 구성해 진행 단계를
단계별로 시각화하고, ChatGPT(LLM)로 이미지 생성 프롬프트를 보강한 뒤
HuggingFace text-to-image 모델로 로고 이미지를 생성하고, 로고를 선택하는
순간 그 로고와 연락처 정보를 Pillow로 합성해 명함 시안을 만듭니다.

학습 진행 순서: **AI → LLM → EDA → ChatGPT+HuggingFace → LangChain/LangGraph**

## 아키텍처

- **백엔드**: FastAPI + LangGraph (`backend/`)
  - `app/graph.py` — 4단계 노드(`collect_input` → `generate_prompt` →
    `generate_logos` → `generate_business_card`)로 구성된 StateGraph.
    `MemorySaver` 체크포인터와 `interrupt_after`를 사용해 "로고 생성"(입력
    확인 → 프롬프트 생성 → 로고 생성까지 한 번에 실행)과 "명함 생성"(로고
    선택 즉시 실행) 두 번의 API 호출에 걸쳐 하나의 그래프 실행을 이어갑니다.
  - `app/services/llm_service.py` — OpenAI(ChatGPT) API로 프롬프트 보강,
    키가 없으면 템플릿 조합으로 자동 대체(fallback).
  - `app/services/image_service.py` — HuggingFace Inference API
    (`text_to_image`)로 로고 3장 생성을 우선 시도하고, 모델이 없어졌거나
    호출이 실패하면 OpenAI Images API(`gpt-image-1`)로 자동 대체, 그마저도
    안 되면(키 없음 등) Pillow로 만든 데모용 플레이스홀더 로고 3종으로
    최종 대체.
  - `app/services/card_service.py` — 선택된 로고 이미지와 이름/직함/전화/
    이메일/주소를 Pillow로 명함 사이즈 캔버스에 합성. 한글 렌더링을 위해
    Nanum Gothic 폰트를 `app/assets/fonts/`에 번들링(OFL-1.1 라이선스).
    외부 API 호출이 없어 항상 안정적으로 동작합니다.
- **프론트엔드**: React + Vite + TypeScript + Tailwind CSS (`frontend/`)
  - 5단계 진행 스테퍼(`StepProgress`), 입력 폼(`LogoForm`, "로고 생성" 버튼
    하나로 프롬프트 생성부터 로고 생성까지 즉시 실행), 프롬프트
    미리보기(`PromptPreview`), 결과 그리드(`ResultsGrid`, 로고를 클릭하면
    그 즉시 명함 생성이 실행됨), 명함 정보 입력(`CardForm`, 별도 제출
    버튼 없이 로고 선택 시점의 값을 사용), 명함 시안 미리보기(`CardPreview`,
    정보 수정 후 재생성 가능)로 구성.

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
| `OPENAI_API_KEY` | ChatGPT 프롬프트 보강 + 로고 이미지 생성(HuggingFace 실패 시 대체)용 | 프롬프트는 템플릿 조합, 이미지는 HuggingFace만 시도 |
| `OPENAI_MODEL` | 프롬프트 보강용 OpenAI 모델 (기본 `gpt-4o-mini`) | - |
| `HF_TOKEN` | HuggingFace Inference API 토큰 | 이미지 생성은 바로 OpenAI(있으면)로 시도 |
| `HF_T2I_MODEL` | text-to-image 모델 (기본 `black-forest-labs/FLUX.1-schnell`) — HuggingFace 무료 추론에서 지원 종료된 모델이면 자동으로 OpenAI로 넘어감 | - |
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

배포된 프론트엔드 주소로 접속해 회사명/슬로건 입력 → "로고 생성" → 로고
시안 클릭까지 정상 동작하는지 확인. 만약 CORS 에러가 뜨면 백엔드의
`FRONTEND_ORIGINS`에 프론트엔드 배포 주소가 정확히 포함되어 있는지 확인하세요.

## API

- `POST /api/logo/generate` — `{ company_name, slogan, industry?, style?, colors? }`
  → `{ thread_id, generated_prompt, prompt_source, images, image_source, steps }`
  (images는 base64 PNG data URL 3개)
- `POST /api/card/generate` — `{ thread_id, logo_index, contact_name?, title?, phone?, email?, address? }`
  → `{ card_image, steps }` (card_image는 base64 PNG data URL)
- `GET /api/health` — 서버 상태 및 실제 API 연동 여부 확인
