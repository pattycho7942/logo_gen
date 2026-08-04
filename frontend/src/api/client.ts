import type {
  CardFormValues,
  GenerateCardResult,
  GenerateLogosResult,
  LogoFormValues,
  LogoStep,
} from '../types'

interface StepApiShape {
  id: string
  label: string
  status: string
}

// In local dev this stays empty so requests hit the Vite dev-server proxy
// (see vite.config.ts). In production the frontend and backend are deployed
// separately, so VITE_API_BASE_URL must point at the deployed backend origin.
const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json()
    if (typeof data.detail === 'string') return data.detail
  } catch {
    // ignore parse failure, fall through to generic message
  }
  return `요청이 실패했습니다 (HTTP ${response.status})`
}

function toSteps(steps: StepApiShape[]): LogoStep[] {
  return steps.map((step) => ({
    id: step.id,
    label: step.label,
    status: step.status as LogoStep['status'],
  }))
}

export async function requestLogoGeneration(
  values: LogoFormValues,
): Promise<GenerateLogosResult> {
  const response = await fetch(`${API_BASE}/api/logo/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company_name: values.companyName,
      slogan: values.slogan,
      industry: values.industry || undefined,
      style: values.style || undefined,
      colors: values.colors || undefined,
    }),
  })

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response))
  }

  const data = await response.json()
  return {
    threadId: data.thread_id,
    generatedPrompt: data.generated_prompt,
    promptSource: data.prompt_source,
    images: data.images,
    imageSource: data.image_source,
    steps: toSteps(data.steps),
  }
}

export async function requestCardGeneration(
  threadId: string,
  logoIndex: number,
  card: CardFormValues,
): Promise<GenerateCardResult> {
  const response = await fetch(`${API_BASE}/api/card/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      thread_id: threadId,
      logo_index: logoIndex,
      contact_name: card.contactName || undefined,
      title: card.title || undefined,
      phone: card.phone || undefined,
      email: card.email || undefined,
      address: card.address || undefined,
      layout: card.layout,
    }),
  })

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response))
  }

  const data = await response.json()
  return {
    cardImage: data.card_image,
    steps: toSteps(data.steps),
  }
}
