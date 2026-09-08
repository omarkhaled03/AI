import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { CreateTripPage } from '../../../src/features/trips/CreateTripPage'

function renderPage() {
  render(
    <MemoryRouter>
      <CreateTripPage />
    </MemoryRouter>,
  )
}

describe('CreateTripPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  it('test_create_form_submits_and_shows_success', async () => {
    const createdTrip = {
      id: 'trip-1',
      destination: 'Paris',
      departure_date: '2026-10-01',
      return_date: '2026-10-10',
      created_at: '2026-09-08T00:00:00Z',
    }
    ;(fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 201,
      text: async () => JSON.stringify(createdTrip),
    })

    renderPage()
    await userEvent.type(screen.getByLabelText(/destination/i), 'Paris')
    await userEvent.type(screen.getByLabelText(/departure date/i), '2026-10-01')
    await userEvent.type(screen.getByLabelText(/return date/i), '2026-10-10')
    await userEvent.click(screen.getByRole('button', { name: /create trip/i }))

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('Trip created successfully')
    })
    expect(screen.getByRole('status')).toHaveTextContent('Paris')
  })

  it('test_create_form_shows_field_error_on_422_for_known_field', async () => {
    ;(fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 422,
      text: async () =>
        JSON.stringify({
          detail: [
            {
              type: 'missing',
              loc: ['body', 'destination'],
              msg: 'Field required',
            },
          ],
        }),
    })

    renderPage()
    // destination intentionally left blank; form uses noValidate so the
    // submit reaches the API and the backend's 422 must be surfaced.
    await userEvent.type(screen.getByLabelText(/departure date/i), '2026-10-01')
    await userEvent.click(screen.getByRole('button', { name: /create trip/i }))

    await waitFor(() => {
      expect(screen.getByText('Field required')).toBeInTheDocument()
    })
  })

  it('test_create_form_blocks_submit_when_return_date_before_departure_date', async () => {
    renderPage()
    await userEvent.type(screen.getByLabelText(/destination/i), 'Paris')
    await userEvent.type(screen.getByLabelText(/departure date/i), '2026-10-10')
    await userEvent.type(screen.getByLabelText(/return date/i), '2026-10-05')
    await userEvent.click(screen.getByRole('button', { name: /create trip/i }))

    await waitFor(() => {
      expect(
        screen.getByText('Return date cannot be before departure date.'),
      ).toBeInTheDocument()
    })
    expect(fetch).not.toHaveBeenCalled()
  })

  it('test_create_form_surfaces_backend_422_for_return_date_before_departure_date', async () => {
    // Client-side check passes here (return_date === departure_date is valid),
    // so this exercises the network path and the handling of the backend's
    // real error shape for the cross-field model validator: loc: ["body"]
    // (no field name), msg prefixed by pydantic with "Value error, ".
    ;(fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 422,
      text: async () =>
        JSON.stringify({
          detail: [
            {
              type: 'value_error',
              loc: ['body'],
              msg: 'Value error, return_date must not be before departure_date',
              input: {
                destination: 'Paris',
                departure_date: '2026-10-10',
                return_date: '2026-10-10',
              },
              ctx: { error: {} },
            },
          ],
        }),
    })

    renderPage()
    await userEvent.type(screen.getByLabelText(/destination/i), 'Paris')
    await userEvent.type(screen.getByLabelText(/departure date/i), '2026-10-10')
    await userEvent.type(screen.getByLabelText(/return date/i), '2026-10-10')
    await userEvent.click(screen.getByRole('button', { name: /create trip/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/return_date must not be before departure_date/),
      ).toBeInTheDocument()
    })
    expect(fetch).toHaveBeenCalledTimes(1)
  })
})
