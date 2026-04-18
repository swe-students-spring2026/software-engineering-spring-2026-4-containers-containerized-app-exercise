import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import RecordPage from './pages/RecordPage'
import ResultsPage from './pages/ResultsPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RecordPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/dashboard" element={<DashboardPage />}/>
      </Routes>
    </Router>
  )
}

export default App