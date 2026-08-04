interface Props {
  cardImage: string
  loading: boolean
  companyName: string
}

export default function CardPreview({ cardImage, loading, companyName }: Props) {
  if (!loading && !cardImage) return null

  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-base font-semibold text-gray-900">명함 시안</h3>
      {loading ? (
        <div className="aspect-[7/4] w-full animate-pulse rounded-2xl bg-gray-100" />
      ) : (
        <div className="flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
          <img
            src={cardImage}
            alt={`${companyName} 명함 시안`}
            className="w-full object-contain"
          />
          <a
            href={cardImage}
            download={`${companyName || 'card'}-명함.png`}
            className="border-t border-gray-100 py-2.5 text-center text-sm font-medium text-violet-600 transition hover:bg-violet-50"
          >
            다운로드
          </a>
        </div>
      )}
    </div>
  )
}
