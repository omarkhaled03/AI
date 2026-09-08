import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../../lib/api'
import { listTrips } from './api'
import type { Trip } from './types'
import styles from './TripListPage.module.css'

const LIMIT = 20

export function TripListPage() {
  const [trips, setTrips] = useState<Trip[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [destinationInput, setDestinationInput] = useState('')
  const [destination, setDestination] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    listTrips({ destination: destination || undefined, limit: LIMIT, offset })
      .then((response) => {
        if (cancelled) return
        setTrips(response.items)
        setTotal(response.total)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Failed to load trips.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [destination, offset])

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setOffset(0)
    setDestination(destinationInput.trim())
  }

  const hasNextPage = offset + LIMIT < total
  const hasPrevPage = offset > 0

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Trips</h1>
      <p>
        <Link to="/trips/new" className={styles.createLink}>
          Create a new trip
        </Link>
      </p>

      <form className={styles.searchBar} onSubmit={handleSearchSubmit}>
        <input
          type="text"
          placeholder="Search by destination"
          aria-label="Search by destination"
          value={destinationInput}
          onChange={(e) => setDestinationInput(e.target.value)}
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
              <th>Destination</th>
              <th>Departure date</th>
              <th>Return date</th>
            </tr>
          </thead>
          <tbody>
            {trips.map((trip) => (
              <tr key={trip.id}>
                <td>{trip.destination}</td>
                <td>{trip.departure_date}</td>
                <td>
                  {trip.return_date ? (
                    trip.return_date
                  ) : (
                    <span className={styles.oneWay}>One-way</span>
                  )}
                </td>
              </tr>
            ))}
            {trips.length === 0 && !error && (
              <tr>
                <td colSpan={3}>No trips found.</td>
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
          Showing {trips.length === 0 ? 0 : offset + 1}-{offset + trips.length} of {total}
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
