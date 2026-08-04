import type { CardFormValues } from '../types'

interface Props {
  values: CardFormValues
  onChange: (values: CardFormValues) => void
  onSubmit: () => void
  loading: boolean
  logoSelected: boolean
}

const FIELDS: { key: keyof CardFormValues; label: string; placeholder: string }[] = [
  { key: 'contactName', label: '이름', placeholder: '예: 홍길동' },
  { key: 'title', label: '직함', placeholder: '예: 대표' },
  { key: 'phone', label: '전화번호', placeholder: '예: 010-1234-5678' },
  { key: 'email', label: '이메일', placeholder: '예: hong@mokabean.kr' },
  { key: 'address', label: '주소', placeholder: '예: 서울시 강남구' },
]

export default function CardForm({ values, onChange, onSubmit, loading, logoSelected }: Props) {
  const update = (patch: Partial<CardFormValues>) => onChange({ ...values, ...patch })

  return (
    <form
      className="flex flex-col gap-6"
      onSubmit={(e) => {
        e.preventDefault()
        if (logoSelected && !loading) onSubmit()
      }}
    >
      <div>
        <h3 className="text-base font-semibold text-gray-900">명함 정보 입력</h3>
        <p className="mt-1 text-xs text-gray-400">
          모두 선택 입력이에요. 위에서 명함에 쓸 로고도 하나 선택해주세요.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {FIELDS.map((field) => (
          <label key={field.key} className="flex flex-col gap-1.5 text-sm font-medium text-gray-700">
            {field.label}
            <input
              className="rounded-xl border border-gray-200 px-4 py-2.5 text-base text-gray-900 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
              placeholder={field.placeholder}
              maxLength={120}
              value={values[field.key]}
              onChange={(e) => update({ [field.key]: e.target.value } as Partial<CardFormValues>)}
            />
          </label>
        ))}
      </div>

      <button
        type="submit"
        disabled={!logoSelected || loading}
        className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-500 px-6 py-3.5 text-base font-semibold text-white shadow-lg shadow-violet-200 transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? '명함 생성 중...' : logoSelected ? '명함 생성' : '위에서 로고를 먼저 선택해주세요'}
      </button>
    </form>
  )
}
