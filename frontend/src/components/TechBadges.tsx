const STACK = ['AI', 'LLM', 'EDA', 'ChatGPT + HuggingFace', 'LangChain / LangGraph']

export default function TechBadges() {
  return (
    <div className="flex flex-col items-center gap-3">
      <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
        이 프로젝트가 거쳐온 학습 스택
      </span>
      <div className="flex flex-wrap items-center justify-center gap-2">
        {STACK.map((item, i) => (
          <span key={item} className="flex items-center gap-2">
            <span className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-600">
              {item}
            </span>
            {i < STACK.length - 1 && <span className="text-gray-300">→</span>}
          </span>
        ))}
      </div>
    </div>
  )
}
