import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../../lib/api'
import { createTrip } from './api'
import type { Trip, ValidationErrorItem } from './types'
import styles from './CreateTripPage.module.css'

interface FormState {
  destination: string
  departure_date: string
  return_date: string
}

const initialFormState: FormState = {
  destination: '',
  departure_date: '',
  return_date: '',
}

const KNOWN_FIELDS = new Set(['destination', 'departure_date', 'return_date'])

export function CreateTripPage() {
  const [form, setForm] = useState<FormState>(initialFormState)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [created, setCreated] = useState<Trip | null>(null)

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFieldErrors({})
    setFormError(null)
    setCreated(null)

    if (form.return_date && form.return_date < form.departure_date) {
      setFormError('Return date cannot be before departure date.')
      return
    }

    setSubmitting(true)

    try {
      const trip = await createTrip({
        destination: form.destination,
        departure_date: form.departure_date,
        return_date: form.return_date.trim() ? form.return_date.trim() : undefined,
      })
      setCreated(trip)
      setForm(initialFormState)
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 422) {
          const body = err.body as { detail?: ValidationErrorItem[] }
          const nextFieldErrors: Record<string, string> = {}
          const generalMessages: string[] = []
          for (const item of body.detail ?? []) {
            const field = item.loc[item.loc.length - 1]
            if (typeof field === 'string' && KNOWN_FIELDS.has(field)) {
              nextFieldErrors[field] = item.msg
            } else {
              generalMessages.push(item.msg)
            }
          }
          setFieldErrors(nextFieldErrors)
          if (generalMessages.length > 0) {
            setFormError(generalMessages.join(' '))
          } else if (Object.keys(nextFieldErrors).length === 0) {
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
      <h1 className={styles.title}>Create Trip</h1>
      <p>
        <Link to="/trips" className={styles.backLink}>
          View trips
        </Link>
      </p>

      {formError && (
        <div className={styles.formError} role="alert">
          {formError}
        </div>
      )}

      {created && (
        <div className={styles.successMessage} role="status">
          Trip created successfully: {created.destination} (id: {created.id})
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className={styles.field}>
          <label htmlFor="destination">Destination</label>
          <input
            id="destination"
            type="text"
            required
            value={form.destination}
            onChange={(e) => updateField('destination', e.target.value)}
          />
          {fieldErrors.destination && (
            <span className={styles.fieldError}>{fieldErrors.destination}</span>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="departure_date">Departure date</label>
          <input
            id="departure_date"
            type="date"
            required
            value={form.departure_date}
            onChange={(e) => updateField('departure_date', e.target.value)}
          />
          {fieldErrors.departure_date && (
            <span className={styles.fieldError}>{fieldErrors.departure_date}</span>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="return_date">Return date (optional)</label>
          <input
            id="return_date"
            type="date"
            value={form.return_date}
            onChange={(e) => updateField('return_date', e.target.value)}
          />
          {fieldErrors.return_date && (
            <span className={styles.fieldError}>{fieldErrors.return_date}</span>
          )}
        </div>

        <button type="submit" className={styles.submitButton} disabled={submitting}>
          {submitting ? 'Creating...' : 'Create trip'}
        </button>
      </form>
    </div>
  )
}
