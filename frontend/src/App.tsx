import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Generator from './pages/Generator'
import History from './pages/History'
import JobDetail from './pages/JobDetail'
import Scheduled from './pages/Scheduled'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Generator />} />
        <Route path="history" element={<History />} />
        <Route path="job/:jobId" element={<JobDetail />} />
        <Route path="scheduled" element={<Scheduled />} />
      </Route>
    </Routes>
  )
}

export default App
