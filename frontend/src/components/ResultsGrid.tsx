interface Props {
  images: string[]
  imageSource: 'huggingface' | 'openai' | 'placeholder'
  loading: boolean
  companyName: string
  selectedIndex: number | null
  onSelect: (index: number) => void
}

const SOURCE_LABEL: Record<Props['imageSource'], string> = {
  huggingface: 'HuggingFace 생성',
  openai: 'OpenAI 생성',
  placeholder: '데모 이미지',
}

function Skeleton() {
  return (
    <div className="aspect-square animate-pulse rounded-2xl bg-gray-100" />
  )
}

export default function ResultsGrid({
  images,
  imageSource,
  loading,
  companyName,
  selectedIndex,
  onSelect,
}: Props) {
  if (!loading && images.length === 0) return null

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900">로고 시안 3종</h3>
        {images.length > 0 && (
          <span
            className={`rounded-full px-2.5 py-1 text-xs font-medium ${
              imageSource === 'placeholder'
                ? 'bg-amber-100 text-amber-700'
                : 'bg-violet-100 text-violet-700'
            }`}
          >
            {SOURCE_LABEL[imageSource]}
          </span>
        )}
      </div>
      {images.length > 0 && (
        <p className="text-xs text-gray-400">로고를 클릭하면 명함 제작에 사용할 로고로 선택돼요.</p>
      )}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {loading
          ? [0, 1, 2].map((i) => <Skeleton key={i} />)
          : images.map((src, i) => {
              const selected = selectedIndex === i
              return (
                <div
                  key={i}
                  className={`flex flex-col overflow-hidden rounded-2xl border bg-white shadow-sm transition ${
                    selected ? 'border-violet-500 ring-2 ring-violet-200' : 'border-gray-200'
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => onSelect(i)}
                    className="relative"
                  >
                    <img
                      src={src}
                      alt={`${companyName} 로고 시안 ${i + 1}`}
                      className="aspect-square w-full object-cover"
                    />
                    {selected && (
                      <span className="absolute right-2 top-2 rounded-full bg-violet-600 px-2 py-0.5 text-[11px] font-semibold text-white shadow">
                        선택됨
                      </span>
                    )}
                  </button>
                  <a
                    href={src}
                    download={`${companyName || 'logo'}-시안${i + 1}.png`}
                    className="border-t border-gray-100 py-2.5 text-center text-sm font-medium text-violet-600 transition hover:bg-violet-50"
                  >
                    다운로드
                  </a>
                </div>
              )
            })}
      </div>
    </div>
  )
}
