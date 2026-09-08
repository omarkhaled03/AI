import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { TripListPage } from '../../../src/features/trips/TripListPage'

function mockFetchOnce(response: {
  ok: boolean
  status: number
  body: unknown
}) {
  ;(fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
    ok: response.ok,
    status: response.status,
    text: async () => JSON.stringify(response.body),
  })
}

function makeTrip(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: '1',
    destination: 'Paris',
    departure_date: '2026-10-01',
    return_date: '2026-10-10',
    created_at: '2026-09-08T00:00:00Z',
    ...overrides,
  }
}

describe('TripListPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  it('test_list_page_renders_fetched_trips', async () => {
    const response = {
      items: [
        makeTrip({ id: '1', destination: 'Paris', departure_date: '2026-10-01', return_date: '2026-10-10' }),
        makeTrip({ id: '2', destination: 'Tokyo', departure_date: '2026-11-05', return_date: null }),
      ],
      total: 2,
      limit: 20,
      offset: 0,
    }
    mockFetchOnce({ ok: true, status: 200, body: response })

    render(
      <MemoryRouter>
        <TripListPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText('Paris')).toBeInTheDocument()
    })
    expect(screen.getByText('Tokyo')).toBeInTheDocument()
    expect(screen.getByText('2026-10-01')).toBeInTheDocument()
    expect(screen.getByText('2026-10-10')).toBeInTheDocument()
    expect(screen.getByText('2026-11-05')).toBeInTheDocument()
    // Trip with no return_date renders a one-way indicator instead of blank/null.
    expect(screen.getByText('One-way')).toBeInTheDocument()
    expect(screen.getByText(/Showing 1-2 of 2/)).toBeInTheDocument()
  })

  it('test_list_page_search_filters_by_destination', async () => {
    mockFetchOnce({
      ok: true,
      status: 200,
      body: { items: [], total: 0, limit: 20, offset: 0 },
    })

    render(
      <MemoryRouter>
        <TripListPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1)
    })

    mockFetchOnce({
      ok: true,
      status: 200,
      body: {
        items: [makeTrip({ id: '3', destination: 'Paris' })],
        total: 1,
        limit: 20,
        offset: 0,
      },
    })

    await userEvent.type(screen.getByLabelText(/search by destination/i), 'Paris')
    await userEvent.click(screen.getByRole('button', { name: /search/i }))

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2)
    })
    const secondCallUrl = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[1][0] as string
    expect(secondCallUrl).toContain('destination=Paris')
  })

  it('test_list_page_pagination_next_button_requests_next_offset', async () => {
    const page1Items = Array.from({ length: 20 }, (_, i) =>
      makeTrip({ id: String(i + 1), destination: `Destination ${i + 1}` }),
    )
    mockFetchOnce({
      ok: true,
      status: 200,
      body: { items: page1Items, total: 45, limit: 20, offset: 0 },
    })

    render(
      <MemoryRouter>
        <TripListPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /next/i })).not.toBeDisabled()
    })

    mockFetchOnce({
      ok: true,
      status: 200,
      body: { items: [], total: 45, limit: 20, offset: 20 },
    })

    await userEvent.click(screen.getByRole('button', { name: /next/i }))

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2)
    })
    const secondCallUrl = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[1][0] as string
    expect(secondCallUrl).toContain('offset=20')
  })
})
