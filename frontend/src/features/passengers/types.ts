export type GovernmentIdType = 'passport' | 'national_id'

export interface PassengerCreate {
  full_name: string
  date_of_birth: string
  email: string
  phone?: string
  government_id_type: GovernmentIdType
  government_id_number: string
}

export interface Passenger {
  id: string
  full_name: string
  date_of_birth: string
  email: string
  phone: string | null
  government_id_type: GovernmentIdType
  government_id_number: string
  created_at: string
}

export interface PassengerListResponse {
  items: Passenger[]
  total: number
  limit: number
  offset: number
}

export interface PassengerListQuery {
  name?: string
  government_id_number?: string
  government_id_type?: GovernmentIdType
  limit?: number
  offset?: number
}

export interface ValidationErrorItem {
  loc: (string | number)[]
  msg: string
  type: string
}

export interface DuplicatePassengerError {
  detail: string
  existing_passenger_id: string
}
