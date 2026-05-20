import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Home, Lock, User } from 'lucide-react'
import { authApi } from '../api/client'
import { authStore } from '../store/authStore'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await authApi.login(username, password)
      authStore.setToken(res.data.access_token)
      navigate('/')
    } catch {
      setError('Неверный логин или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl" />
      </div>
      <div className="relative bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-sm border border-gray-700">
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 bg-sky-500 rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-sky-900/40">
            <Home aria-hidden="true" size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">HomeIQ</h1>
          <p className="text-sm text-gray-400 mt-1">Система управления умным домом</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <User size={16} aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <label htmlFor="login-username" className="sr-only">Логин</label>
            <input id="login-username" type="text" placeholder="Логин" value={username}
              autoComplete="username"
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-xl border border-gray-600 bg-gray-700 py-2.5 pl-10 pr-4 text-white placeholder-gray-500 focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800" />
          </div>
          <div className="relative">
            <Lock size={16} aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <label htmlFor="login-password" className="sr-only">Пароль</label>
            <input id="login-password" type="password" placeholder="Пароль" value={password}
              autoComplete="current-password"
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-gray-600 bg-gray-700 py-2.5 pl-10 pr-4 text-white placeholder-gray-500 focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800" />
          </div>
          {error && <p role="alert" className="text-red-400 text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full rounded-xl bg-sky-500 py-2.5 font-semibold text-white transition-colors hover:bg-sky-600 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50">
            {loading ? 'Входим...' : 'Войти'}
          </button>
        </form>
      </div>
    </div>
  )
}
