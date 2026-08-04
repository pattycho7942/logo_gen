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

export interface GenerateLogosResult {
  threadId: string
  generatedPrompt: string
  promptSource: 'llm' | 'template'
  images: string[]
  imageSource: 'huggingface' | 'openai' | 'placeholder'
  steps: LogoStep[]
}

export interface CardFormValues {
  contactName: string
  title: string
  phone: string
  email: string
  address: string
}

export interface GenerateCardResult {
  cardImage: string
  steps: LogoStep[]
}
