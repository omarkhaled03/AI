import { Navigate, Route, Routes } from 'react-router-dom'
import { BrowserRouter } from 'react-router-dom'
import { CreatePassengerPage } from './features/passengers/CreatePassengerPage'
import { PassengerListPage } from './features/passengers/PassengerListPage'
import { CreateTripPage } from './features/trips/CreateTripPage'
import { TripListPage } from './features/trips/TripListPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/passengers" replace />} />
        <Route path="/passengers" element={<PassengerListPage />} />
        <Route path="/passengers/new" element={<CreatePassengerPage />} />
        <Route path="/trips" element={<TripListPage />} />
        <Route path="/trips/new" element={<CreateTripPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
