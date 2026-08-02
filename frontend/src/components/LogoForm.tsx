import type { LogoFormValues } from '../types'

const INDUSTRY_OPTIONS = [
  '카페 · 음식점',
  '패션 · 뷰티',
  'IT · 테크',
  '헬스케어',
  '교육',
  '금융',
  '기타',
]

const STYLE_OPTIONS = [
  '미니멀',
  '엠블럼',
  '모던',
  '빈티지 · 레트로',
  '캐릭터 · 마스코트',
  '타이포그래피 중심',
]

const COLOR_OPTIONS: { label: string; value: string; swatch: [string, string] }[] = [
  { label: '블루 & 퍼플', value: 'blue and purple', swatch: ['#3b82f6', '#8b5cf6'] },
  { label: '그린 & 민트', value: 'green and mint', swatch: ['#22c55e', '#2dd4bf'] },
  { label: '레드 & 오렌지', value: 'red and orange', swatch: ['#ef4444', '#f97316'] },
  { label: '블랙 & 골드', value: 'black and gold', swatch: ['#111827', '#eab308'] },
  { label: '파스텔', value: 'soft pastel tones', swatch: ['#fbcfe8', '#c7d2fe'] },
]

interface Props {
  values: LogoFormValues
  onChange: (values: LogoFormValues) => void
  onSubmit: () => void
  loading: boolean
}

export default function LogoForm({ values, onChange, onSubmit, loading }: Props) {
  const update = (patch: Partial<LogoFormValues>) => onChange({ ...values, ...patch })

  const canSubmit = values.companyName.trim().length > 0 && values.slogan.trim().length > 0

  return (
    <form
      className="flex flex-col gap-6"
      onSubmit={(e) => {
        e.preventDefault()
        if (canSubmit && !loading) onSubmit()
      }}
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-700">
          회사명 <span className="text-violet-500">*</span>
          <input
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-base text-gray-900 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
            placeholder="예: 모카빈"
            maxLength={60}
            value={values.companyName}
            onChange={(e) => update({ companyName: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-700">
          슬로건 <span className="text-violet-500">*</span>
          <input
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-base text-gray-900 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
            placeholder="예: 매일 아침의 행복"
            maxLength={120}
            value={values.slogan}
            onChange={(e) => update({ slogan: e.target.value })}
          />
        </label>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-700">
          업종 <span className="font-normal text-gray-400">(선택)</span>
          <select
            className="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-base text-gray-900 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
            value={values.industry}
            onChange={(e) => update({ industry: e.target.value })}
          >
            <option value="">선택 안 함</option>
            {INDUSTRY_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-700">
          스타일 <span className="font-normal text-gray-400">(선택)</span>
          <select
            className="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-base text-gray-900 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
            value={values.style}
            onChange={(e) => update({ style: e.target.value })}
          >
            <option value="">선택 안 함</option>
            {STYLE_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium text-gray-700">
          색상 <span className="font-normal text-gray-400">(선택)</span>
        </span>
        <div className="flex flex-wrap gap-2">
          {COLOR_OPTIONS.map((opt) => {
            const selected = values.colors === opt.value
            return (
              <button
                type="button"
                key={opt.value}
                onClick={() => update({ colors: selected ? '' : opt.value })}
                className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm transition ${
                  selected
                    ? 'border-violet-500 bg-violet-50 text-violet-700'
                    : 'border-gray-200 text-gray-600 hover:border-violet-300'
                }`}
              >
                <span
                  className="h-3.5 w-3.5 rounded-full"
                  style={{
                    background: `linear-gradient(135deg, ${opt.swatch[0]}, ${opt.swatch[1]})`,
                  }}
                />
                {opt.label}
              </button>
            )
          })}
        </div>
      </div>

      <button
        type="submit"
        disabled={!canSubmit || loading}
        className="mt-2 w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-500 px-6 py-3.5 text-base font-semibold text-white shadow-lg shadow-violet-200 transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? '프롬프트 생성 중...' : '프롬프트 생성'}
      </button>
    </form>
  )
}
