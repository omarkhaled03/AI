import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../../lib/api'
import { listPassengers } from './api'
import type { Passenger } from './types'
import styles from './PassengerListPage.module.css'

const LIMIT = 20

export function PassengerListPage() {
  const [passengers, setPassengers] = useState<Passenger[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [nameInput, setNameInput] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    listPassengers({ name: name || undefined, limit: LIMIT, offset })
      .then((response) => {
        if (cancelled) return
        setPassengers(response.items)
        setTotal(response.total)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Failed to load passengers.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [name, offset])

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setOffset(0)
    setName(nameInput.trim())
  }

  const hasNextPage = offset + LIMIT < total
  const hasPrevPage = offset > 0

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Passengers</h1>
      <p>
        <Link to="/passengers/new" className={styles.createLink}>
          Create a new passenger
        </Link>
      </p>

      <form className={styles.searchBar} onSubmit={handleSearchSubmit}>
        <input
          type="text"
          placeholder="Search by name"
          aria-label="Search by name"
          value={nameInput}
          onChange={(e) => setNameInput(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      {error && (
        <div className={styles.errorMessage} role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Full name</th>
              <th>Date of birth</th>
              <th>Email</th>
              <th>Government ID</th>
            </tr>
          </thead>
          <tbody>
            {passengers.map((passenger) => (
              <tr key={passenger.id}>
                <td>{passenger.full_name}</td>
                <td>{passenger.date_of_birth}</td>
                <td>{passenger.email}</td>
                <td>
                  <span
                    className={`${styles.idBadge} ${
                      passenger.government_id_type === 'passport'
                        ? styles.idBadgePassport
                        : styles.idBadgeNationalId
                    }`}
                  >
                    {passenger.government_id_type}
                  </span>{' '}
                  {passenger.government_id_number}
                </td>
              </tr>
            ))}
            {passengers.length === 0 && !error && (
              <tr>
                <td colSpan={4}>No passengers found.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      <div className={styles.pagination}>
        <button
          type="button"
          disabled={!hasPrevPage}
          onClick={() => setOffset((prev) => Math.max(0, prev - LIMIT))}
        >
          Previous
        </button>
        <span>
          Showing {passengers.length === 0 ? 0 : offset + 1}-{offset + passengers.length} of {total}
        </span>
        <button
          type="button"
          disabled={!hasNextPage}
          onClick={() => setOffset((prev) => prev + LIMIT)}
        >
          Next
        </button>
      </div>
    </div>
  )
}
