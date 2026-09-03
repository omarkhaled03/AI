import { apiRequest } from '../../lib/api'
import type { Passenger, PassengerCreate, PassengerListQuery, PassengerListResponse } from './types'

export function createPassenger(data: PassengerCreate): Promise<Passenger> {
  return apiRequest<Passenger>('/passengers', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function listPassengers(query: PassengerListQuery = {}): Promise<PassengerListResponse> {
  const params = new URLSearchParams()
  if (query.name) params.set('name', query.name)
  if (query.government_id_number) params.set('government_id_number', query.government_id_number)
  if (query.government_id_type) params.set('government_id_type', query.government_id_type)
  params.set('limit', String(query.limit ?? 20))
  params.set('offset', String(query.offset ?? 0))

  return apiRequest<PassengerListResponse>(`/passengers?${params.toString()}`)
}
