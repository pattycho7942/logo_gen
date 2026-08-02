import type {
  GenerateLogosResult,
  GeneratePromptResult,
  LogoFormValues,
  LogoStep,
} from '../types'

interface StepApiShape {
  id: string
  label: string
  status: string
}

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

export async function requestPromptGeneration(
  values: LogoFormValues,
): Promise<GeneratePromptResult> {
  const response = await fetch('/api/prompt/generate', {
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
    steps: toSteps(data.steps),
  }
}

export async function requestLogoGeneration(
  threadId: string,
): Promise<GenerateLogosResult> {
  const response = await fetch('/api/logo/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_id: threadId }),
  })

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response))
  }

  const data = await response.json()
  return {
    images: data.images,
    imageSource: data.image_source,
    steps: toSteps(data.steps),
  }
}
