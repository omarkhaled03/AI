export interface TripCreate {
  destination: string
  departure_date: string
  return_date?: string
}

export interface Trip {
  id: string
  destination: string
  departure_date: string
  return_date: string | null
  created_at: string
}

export interface TripListResponse {
  items: Trip[]
  total: number
  limit: number
  offset: number
}

export interface TripListQuery {
  destination?: string
  limit?: number
  offset?: number
}

export interface ValidationErrorItem {
  loc: (string | number)[]
  msg: string
  type: string
}
