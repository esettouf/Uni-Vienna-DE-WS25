import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/home/Home'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Identity from './pages/auth/Identity'
import Certificates from './pages/certification/Certificates'
import CertSubmit from './pages/certification/CertSubmit'
import CertRequests from './pages/certification/CertRequests'
import CertRequestDetail from './pages/certification/CertRequestDetail'
import SellOrders from './pages/trading/SellOrders'
import SellCreate from './pages/trading/SellCreate'
import Bids from './pages/trading/Bids'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminUsers from './pages/admin/AdminUsers'
import AdminCertRequests from './pages/admin/AdminCertRequests'
import AdminCertRequestDetail from './pages/admin/AdminCertRequestDetail'
import Layout from './components/Layout'
import GuardRoute from './components/GuardRoute'
import MarketOverview from './pages/trading/MarketOverview'
import AdminTrades from './pages/admin/AdminTrades'

import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/identity"
            element={
              // GuardRoute defines which roles can view this component
              <GuardRoute>
                <Identity />
              </GuardRoute>
            }
          />
          <Route
            path="/certificates"
            element={
              <GuardRoute>
                <Certificates />
              </GuardRoute>
            }
          />
          <Route
            path="/certification/submit"
            element={
              <GuardRoute>
                <CertSubmit />
              </GuardRoute>
            }
          />
          <Route
            path="/certification/requests"
            element={
              <GuardRoute>
                <CertRequests />
              </GuardRoute>
            }
          />
          <Route
            path="/certification/requests/:id"
            element={
              <GuardRoute>
                <CertRequestDetail />
              </GuardRoute>
            }
          />
          <Route
            path="/trading"
            element={
              <GuardRoute>
                <SellOrders />
              </GuardRoute>
            }
          />
          <Route
            path="/market"
            element={
              <GuardRoute>
                <MarketOverview />
              </GuardRoute>
            }
          />
          <Route
            path="/trading/sell-create"
            element={
              <GuardRoute>
                <SellCreate />
              </GuardRoute>
            }
          />
          <Route
            path="/trading/bids"
            element={
              <GuardRoute allowedRoles={["business"]}>
                <Bids />
              </GuardRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <GuardRoute requiredRole="admin">
                <AdminDashboard />
              </GuardRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <GuardRoute requiredRole="admin">
                <AdminUsers />
              </GuardRoute>
            }
          />
          <Route
            path="/admin/cert-requests"
            element={
              <GuardRoute requiredRole="admin">
                <AdminCertRequests />
              </GuardRoute>
            }
          />
          <Route
            path="/admin/cert-requests/:id"
            element={
              <GuardRoute requiredRole="admin">
                <AdminCertRequestDetail />
              </GuardRoute>
            }
          />
          <Route
            path="/admin/trades"
            element={
              <GuardRoute requiredRole="admin">
                <AdminTrades />
              </GuardRoute>
            }
          />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
