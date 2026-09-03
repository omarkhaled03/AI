import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { PassengerListPage } from '../../../src/features/passengers/PassengerListPage'

describe('PassengerListPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  it('test_list_page_renders_fetched_passengers', async () => {
    const response = {
      items: [
        {
          id: '1',
          full_name: 'Jane Doe',
          date_of_birth: '1990-01-01',
          email: 'jane@example.com',
          phone: null,
          government_id_type: 'passport',
          government_id_number: 'A1234567',
          created_at: '2026-09-03T00:00:00Z',
        },
        {
          id: '2',
          full_name: 'John Smith',
          date_of_birth: '1985-05-05',
          email: 'john@example.com',
          phone: '123456',
          government_id_type: 'national_id',
          government_id_number: 'B7654321',
          created_at: '2026-09-03T00:00:00Z',
        },
      ],
      total: 2,
      limit: 20,
      offset: 0,
    }

    ;(fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 200,
      text: async () => JSON.stringify(response),
    })

    render(
      <MemoryRouter>
        <PassengerListPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText('Jane Doe')).toBeInTheDocument()
    })
    expect(screen.getByText('John Smith')).toBeInTheDocument()
    expect(screen.getByText(/Showing 1-2 of 2/)).toBeInTheDocument()
  })
})
