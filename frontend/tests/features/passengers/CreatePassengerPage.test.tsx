import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { CreatePassengerPage } from '../../../src/features/passengers/CreatePassengerPage'

function renderPage() {
  render(
    <MemoryRouter>
      <CreatePassengerPage />
    </MemoryRouter>,
  )
}

async function fillForm() {
  await userEvent.type(screen.getByLabelText(/full name/i), 'Jane Doe')
  await userEvent.type(screen.getByLabelText(/date of birth/i), '1990-01-01')
  await userEvent.type(screen.getByLabelText(/email/i), 'jane@example.com')
  await userEvent.type(screen.getByLabelText(/government id number/i), 'A1234567')
  await userEvent.click(screen.getByRole('button', { name: /create passenger/i }))
}

describe('CreatePassengerPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  it('test_create_form_submits_and_shows_success', async () => {
    const createdPassenger = {
      id: 'abc-123',
      full_name: 'Jane Doe',
      date_of_birth: '1990-01-01',
      email: 'jane@example.com',
      phone: null,
      government_id_type: 'passport',
      government_id_number: 'A1234567',
      created_at: '2026-09-03T00:00:00Z',
    }
    ;(fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 201,
      text: async () => JSON.stringify(createdPassenger),
    })

    renderPage()
    await fillForm()

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('Passenger created successfully')
    })
    expect(screen.getByRole('status')).toHaveTextContent('Jane Doe')
  })

  it('test_create_form_shows_duplicate_error_on_409', async () => {
    ;(fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 409,
      text: async () =>
        JSON.stringify({
          detail: 'Passenger with this government id already exists',
          existing_passenger_id: 'existing-id-456',
        }),
    })

    renderPage()
    await fillForm()

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Passenger with this government id already exists',
      )
    })
    expect(screen.getByRole('alert')).toHaveTextContent('existing-id-456')
  })
})
