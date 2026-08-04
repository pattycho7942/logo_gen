import type { CardFormValues, CardLayout } from '../types'

interface Props {
  values: CardFormValues
  onChange: (values: CardFormValues) => void
}

const FIELDS: { key: keyof CardFormValues; label: string; placeholder: string }[] = [
  { key: 'contactName', label: '이름', placeholder: '예: 홍길동' },
  { key: 'title', label: '직함', placeholder: '예: 대표' },
  { key: 'phone', label: '전화번호', placeholder: '예: 010-1234-5678' },
  { key: 'email', label: '이메일', placeholder: '예: hong@mokabean.kr' },
  { key: 'address', label: '주소', placeholder: '예: 서울시 강남구' },
]

const LAYOUT_OPTIONS: { value: CardLayout; label: string }[] = [
  { value: 'classic', label: '기본형' },
  { value: 'centered', label: '중앙 정렬형' },
  { value: 'side_panel', label: '컬러 패널형' },
]

export default function CardForm({ values, onChange }: Props) {
  const update = (patch: Partial<CardFormValues>) => onChange({ ...values, ...patch })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h3 className="text-base font-semibold text-gray-900">명함 정보 입력</h3>
        <p className="mt-1 text-xs text-gray-400">
          모두 선택 입력이에요. 아래에서 로고 시안을 고르면 이 정보로 명함이 바로 만들어져요.
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
              value={values[field.key] as string}
              onChange={(e) => update({ [field.key]: e.target.value } as Partial<CardFormValues>)}
            />
          </label>
        ))}
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium text-gray-700">명함 레이아웃</span>
        <div className="flex flex-wrap gap-2">
          {LAYOUT_OPTIONS.map((opt) => {
            const selected = values.layout === opt.value
            return (
              <button
                type="button"
                key={opt.value}
                onClick={() => update({ layout: opt.value })}
                className={`rounded-full border px-3 py-1.5 text-sm transition ${
                  selected
                    ? 'border-violet-500 bg-violet-50 text-violet-700'
                    : 'border-gray-200 text-gray-600 hover:border-violet-300'
                }`}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
