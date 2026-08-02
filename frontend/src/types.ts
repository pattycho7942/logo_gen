export type StepStatus = 'pending' | 'active' | 'done'

export interface LogoStep {
  id: string
  label: string
  status: StepStatus
}

export interface LogoFormValues {
  companyName: string
  slogan: string
  industry: string
  style: string
  colors: string
}

export interface GeneratePromptResult {
  threadId: string
  generatedPrompt: string
  promptSource: 'llm' | 'template'
  steps: LogoStep[]
}

export interface GenerateLogosResult {
  images: string[]
  imageSource: 'huggingface' | 'openai' | 'placeholder'
  steps: LogoStep[]
}
