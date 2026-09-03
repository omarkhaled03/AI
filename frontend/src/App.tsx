import { Navigate, Route, Routes } from 'react-router-dom'
import { BrowserRouter } from 'react-router-dom'
import { CreatePassengerPage } from './features/passengers/CreatePassengerPage'
import { PassengerListPage } from './features/passengers/PassengerListPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/passengers" replace />} />
        <Route path="/passengers" element={<PassengerListPage />} />
        <Route path="/passengers/new" element={<CreatePassengerPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
