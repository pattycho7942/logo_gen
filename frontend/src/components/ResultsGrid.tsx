interface Props {
  images: string[]
  imageSource: 'huggingface' | 'placeholder'
  loading: boolean
  companyName: string
}

function Skeleton() {
  return (
    <div className="aspect-square animate-pulse rounded-2xl bg-gray-100" />
  )
}

export default function ResultsGrid({ images, imageSource, loading, companyName }: Props) {
  if (!loading && images.length === 0) return null

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900">로고 시안 3종</h3>
        {images.length > 0 && (
          <span
            className={`rounded-full px-2.5 py-1 text-xs font-medium ${
              imageSource === 'huggingface'
                ? 'bg-violet-100 text-violet-700'
                : 'bg-amber-100 text-amber-700'
            }`}
          >
            {imageSource === 'huggingface' ? 'HuggingFace 생성' : '데모 이미지'}
          </span>
        )}
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {loading
          ? [0, 1, 2].map((i) => <Skeleton key={i} />)
          : images.map((src, i) => (
              <div
                key={i}
                className="flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm"
              >
                <img
                  src={src}
                  alt={`${companyName} 로고 시안 ${i + 1}`}
                  className="aspect-square w-full object-cover"
                />
                <a
                  href={src}
                  download={`${companyName || 'logo'}-시안${i + 1}.png`}
                  className="border-t border-gray-100 py-2.5 text-center text-sm font-medium text-violet-600 transition hover:bg-violet-50"
                >
                  다운로드
                </a>
              </div>
            ))}
      </div>
    </div>
  )
}
