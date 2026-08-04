interface Props {
  prompt: string
  promptSource: 'llm' | 'template'
}

export default function PromptPreview({ prompt, promptSource }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900">생성된 이미지 프롬프트</h3>
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
            promptSource === 'llm'
              ? 'bg-violet-100 text-violet-700'
              : 'bg-amber-100 text-amber-700'
          }`}
        >
          {promptSource === 'llm' ? 'ChatGPT로 보강됨' : '템플릿 모드 (데모)'}
        </span>
      </div>
      <p className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm leading-relaxed text-gray-700">
        {prompt}
      </p>
    </div>
  )
}
