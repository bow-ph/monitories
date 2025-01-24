import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './api/client'
import { ThemeProvider } from './contexts/ThemeContext'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import ProjectAnalysis from './pages/ProjectAnalysis'
import PackageSelection from './pages/PackageSelection'
import PackageAdmin from './pages/admin/PackageAdmin'
import AdminClients from './pages/admin/AdminClients'
import AccountSettings from './pages/AccountSettings'
import { Toast } from './components/ui/toast'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="analysis" element={<ProjectAnalysis />} />
              <Route path="packages" element={<PackageSelection />} />
              <Route path="admin/packages" element={<PackageAdmin />} />
              <Route path="admin/clients" element={<AdminClients />} />
              <Route path="account" element={<AccountSettings />} />
            </Route>
          </Routes>
          <Toast />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
