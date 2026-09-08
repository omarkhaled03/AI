import { apiRequest } from '../../lib/api'
import type { Trip, TripCreate, TripListQuery, TripListResponse } from './types'

export function createTrip(data: TripCreate): Promise<Trip> {
  return apiRequest<Trip>('/trips', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function listTrips(query: TripListQuery = {}): Promise<TripListResponse> {
  const params = new URLSearchParams()
  if (query.destination) params.set('destination', query.destination)
  params.set('limit', String(query.limit ?? 20))
  params.set('offset', String(query.offset ?? 0))

  return apiRequest<TripListResponse>(`/trips?${params.toString()}`)
}
