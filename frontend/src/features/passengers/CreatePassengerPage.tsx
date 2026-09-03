import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../../lib/api'
import { createPassenger } from './api'
import type { GovernmentIdType, Passenger, ValidationErrorItem } from './types'
import styles from './CreatePassengerPage.module.css'

interface FormState {
  full_name: string
  date_of_birth: string
  email: string
  phone: string
  government_id_type: GovernmentIdType
  government_id_number: string
}

const initialFormState: FormState = {
  full_name: '',
  date_of_birth: '',
  email: '',
  phone: '',
  government_id_type: 'passport',
  government_id_number: '',
}

export function CreatePassengerPage() {
  const [form, setForm] = useState<FormState>(initialFormState)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [duplicateId, setDuplicateId] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [created, setCreated] = useState<Passenger | null>(null)

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFieldErrors({})
    setFormError(null)
    setDuplicateId(null)
    setCreated(null)
    setSubmitting(true)

    try {
      const passenger = await createPassenger({
        full_name: form.full_name,
        date_of_birth: form.date_of_birth,
        email: form.email,
        phone: form.phone.trim() ? form.phone.trim() : undefined,
        government_id_type: form.government_id_type,
        government_id_number: form.government_id_number,
      })
      setCreated(passenger)
      setForm(initialFormState)
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409) {
          const body = err.body as { detail?: string; existing_passenger_id?: string }
          setFormError(body.detail ?? 'This passenger already exists.')
          setDuplicateId(body.existing_passenger_id ?? null)
        } else if (err.status === 422) {
          const body = err.body as { detail?: ValidationErrorItem[] }
          const nextFieldErrors: Record<string, string> = {}
          for (const item of body.detail ?? []) {
            const field = item.loc[item.loc.length - 1]
            if (typeof field === 'string') {
              nextFieldErrors[field] = item.msg
            }
          }
          setFieldErrors(nextFieldErrors)
          if (Object.keys(nextFieldErrors).length === 0) {
            setFormError('Please fix the errors below and try again.')
          }
        } else {
          setFormError(err.message)
        }
      } else {
        setFormError('Something went wrong. Please try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className={styles.container}>
      <h1>Create Passenger</h1>
      <p>
        <Link to="/passengers">View passengers</Link>
      </p>

      {formError && (
        <div className={styles.formError} role="alert">
          {formError}
          {duplicateId && (
            <>
              {' '}
              Existing passenger id: <strong>{duplicateId}</strong>
            </>
          )}
        </div>
      )}

      {created && (
        <div className={styles.successMessage} role="status">
          Passenger created successfully: {created.full_name} (id: {created.id})
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className={styles.field}>
          <label htmlFor="full_name">Full name</label>
          <input
            id="full_name"
            type="text"
            required
            value={form.full_name}
            onChange={(e) => updateField('full_name', e.target.value)}
          />
          {fieldErrors.full_name && (
            <span className={styles.fieldError}>{fieldErrors.full_name}</span>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="date_of_birth">Date of birth</label>
          <input
            id="date_of_birth"
            type="date"
            required
            value={form.date_of_birth}
            onChange={(e) => updateField('date_of_birth', e.target.value)}
          />
          {fieldErrors.date_of_birth && (
            <span className={styles.fieldError}>{fieldErrors.date_of_birth}</span>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => updateField('email', e.target.value)}
          />
          {fieldErrors.email && <span className={styles.fieldError}>{fieldErrors.email}</span>}
        </div>

        <div className={styles.field}>
          <label htmlFor="phone">Phone (optional)</label>
          <input
            id="phone"
            type="tel"
            value={form.phone}
            onChange={(e) => updateField('phone', e.target.value)}
          />
          {fieldErrors.phone && <span className={styles.fieldError}>{fieldErrors.phone}</span>}
        </div>

        <div className={styles.field}>
          <label htmlFor="government_id_type">Government ID type</label>
          <select
            id="government_id_type"
            value={form.government_id_type}
            onChange={(e) => updateField('government_id_type', e.target.value as GovernmentIdType)}
          >
            <option value="passport">Passport</option>
            <option value="national_id">National ID</option>
          </select>
          {fieldErrors.government_id_type && (
            <span className={styles.fieldError}>{fieldErrors.government_id_type}</span>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="government_id_number">Government ID number</label>
          <input
            id="government_id_number"
            type="text"
            required
            value={form.government_id_number}
            onChange={(e) => updateField('government_id_number', e.target.value)}
          />
          {fieldErrors.government_id_number && (
            <span className={styles.fieldError}>{fieldErrors.government_id_number}</span>
          )}
        </div>

        <button type="submit" className={styles.submitButton} disabled={submitting}>
          {submitting ? 'Creating...' : 'Create passenger'}
        </button>
      </form>
    </div>
  )
}
