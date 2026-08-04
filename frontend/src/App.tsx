import { useState } from 'react'
import { requestCardGeneration, requestLogoGeneration } from './api/client'
import CardForm from './components/CardForm'
import CardPreview from './components/CardPreview'
import LogoForm from './components/LogoForm'
import PromptPreview from './components/PromptPreview'
import ResultsGrid from './components/ResultsGrid'
import StepProgress from './components/StepProgress'
import TechBadges from './components/TechBadges'
import type { CardFormValues, LogoFormValues, LogoStep } from './types'

const DEFAULT_STEPS: LogoStep[] = [
  { id: 'collect_input', label: '입력 확인', status: 'pending' },
  { id: 'generate_prompt', label: 'AI 프롬프트 생성 (ChatGPT)', status: 'pending' },
  { id: 'generate_logos', label: '로고 이미지 생성 (HuggingFace)', status: 'pending' },
  { id: 'generate_business_card', label: '명함 생성 (Pillow)', status: 'pending' },
  { id: 'done', label: '완료', status: 'pending' },
]

const DEFAULT_VALUES: LogoFormValues = {
  companyName: '',
  slogan: '',
  industry: '',
  style: '',
  colors: '',
}

const DEFAULT_CARD_VALUES: CardFormValues = {
  contactName: '',
  title: '',
  phone: '',
  email: '',
  address: '',
  layout: 'classic',
}

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-3xl border border-gray-100 bg-white p-6 shadow-sm shadow-gray-100 sm:p-8">
      {children}
    </div>
  )
}

export default function App() {
  const [formValues, setFormValues] = useState<LogoFormValues>(DEFAULT_VALUES)
  const [steps, setSteps] = useState<LogoStep[]>(DEFAULT_STEPS)
  const [threadId, setThreadId] = useState<string | null>(null)
  const [generatedPrompt, setGeneratedPrompt] = useState('')
  const [promptSource, setPromptSource] = useState<'llm' | 'template'>('template')
  const [images, setImages] = useState<string[]>([])
  const [imageSource, setImageSource] = useState<'huggingface' | 'openai' | 'placeholder'>('placeholder')
  const [selectedLogoIndex, setSelectedLogoIndex] = useState<number | null>(null)
  const [cardValues, setCardValues] = useState<CardFormValues>(DEFAULT_CARD_VALUES)
  const [cardImage, setCardImage] = useState<string>('')
  const [isGeneratingLogos, setIsGeneratingLogos] = useState(false)
  const [isGeneratingCard, setIsGeneratingCard] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const displaySteps = steps.map((step) => {
    if (
      isGeneratingLogos &&
      (step.id === 'generate_prompt' || step.id === 'generate_logos') &&
      step.status === 'pending'
    ) {
      return { ...step, status: 'active' as const }
    }
    if (isGeneratingCard && step.id === 'generate_business_card' && step.status === 'pending') {
      return { ...step, status: 'active' as const }
    }
    return step
  })

  async function handleGenerateLogos() {
    setErrorMessage(null)
    setIsGeneratingLogos(true)
    setImages([])
    setSelectedLogoIndex(null)
    setCardImage('')
    try {
      const result = await requestLogoGeneration(formValues)
      setThreadId(result.threadId)
      setGeneratedPrompt(result.generatedPrompt)
      setPromptSource(result.promptSource)
      setImages(result.images)
      setImageSource(result.imageSource)
      setSteps(result.steps)
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : '로고 생성에 실패했습니다.')
    } finally {
      setIsGeneratingLogos(false)
    }
  }

  async function handleGenerateCard(logoIndex: number) {
    if (!threadId) return
    setErrorMessage(null)
    setSelectedLogoIndex(logoIndex)
    setIsGeneratingCard(true)
    try {
      const result = await requestCardGeneration(threadId, logoIndex, cardValues)
      setCardImage(result.cardImage)
      setSteps(result.steps)
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : '명함 생성에 실패했습니다.')
    } finally {
      setIsGeneratingCard(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f7f6fb]">
      <header className="border-b border-gray-100 bg-white/70 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center gap-2 px-4 py-4 sm:px-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-500 text-sm font-bold text-white">
            L
          </div>
          <span className="text-lg font-bold text-gray-900">LogoGen AI</span>
        </div>
      </header>

      <main className="relative mx-auto max-w-3xl px-4 pb-24 pt-14 sm:px-6">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-72 bg-gradient-to-b from-violet-100 via-violet-50 to-transparent blur-2xl"
        />

        <div className="mb-10 flex flex-col items-center gap-3 text-center">
          <span className="rounded-full bg-violet-100 px-3 py-1 text-xs font-semibold text-violet-700">
            AI 로고 자동 생성
          </span>
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
            AI가 만드는 우리 회사 로고
          </h1>
          <p className="max-w-lg text-sm text-gray-500 sm:text-base">
            회사명과 슬로건만 입력하면 AI가 로고 시안 3가지를 한 번에 만들어드려요.
            마음에 드는 로고를 고르면 그 자리에서 명함까지 바로 완성돼요.
          </p>
        </div>

        <div className="mb-8">
          <Card>
            <StepProgress steps={displaySteps} />
          </Card>
        </div>

        <div className="flex flex-col gap-8">
          <Card>
            <LogoForm
              values={formValues}
              onChange={setFormValues}
              onSubmit={handleGenerateLogos}
              loading={isGeneratingLogos}
            />
          </Card>

          {errorMessage && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorMessage}
            </div>
          )}

          {generatedPrompt && !isGeneratingLogos && (
            <Card>
              <PromptPreview prompt={generatedPrompt} promptSource={promptSource} />
            </Card>
          )}

          {(images.length > 0 || isGeneratingLogos) && (
            <Card>
              <ResultsGrid
                images={images}
                imageSource={imageSource}
                loading={isGeneratingLogos}
                companyName={formValues.companyName}
                selectedIndex={selectedLogoIndex}
                onSelect={handleGenerateCard}
                cardLoading={isGeneratingCard}
              />
            </Card>
          )}

          {images.length > 0 && !isGeneratingLogos && (
            <Card>
              <CardForm values={cardValues} onChange={setCardValues} />
            </Card>
          )}

          {(cardImage || isGeneratingCard) && (
            <Card>
              <CardPreview
                cardImage={cardImage}
                loading={isGeneratingCard}
                companyName={formValues.companyName}
                onRegenerate={() => selectedLogoIndex !== null && handleGenerateCard(selectedLogoIndex)}
              />
            </Card>
          )}
        </div>
      </main>

      <footer className="border-t border-gray-100 bg-white py-10">
        <TechBadges />
      </footer>
    </div>
  )
}
