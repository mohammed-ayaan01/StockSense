import { useState } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { authApi } from '../api'
import { Package, ArrowLeft } from 'lucide-react'

type Step = 'email' | 'otp' | 'success'

export default function ForgotPassword() {
  const [step, setStep] = useState<Step>('email')
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [otpDebug, setOtpDebug] = useState<string | null>(null)

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authApi.forgotPassword(email)
      if (res.data.otp_debug) {
        setOtpDebug(res.data.otp_debug)
        toast.success('OTP generated (shown below for demo)')
      } else {
        toast.success('OTP sent!')
      }
      setStep('otp')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to send OTP')
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword.length < 6) {
      toast.error('Password must be at least 6 characters')
      return
    }
    setLoading(true)
    try {
      await authApi.resetPassword(email, otp, newPassword)
      toast.success('Password reset successfully!')
      setStep('success')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Invalid or expired OTP')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-blue-600 p-2 rounded-xl">
            <Package className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Reset Password</h1>
            <p className="text-sm text-gray-500">StockSense</p>
          </div>
        </div>

        {/* Step indicators */}
        <div className="flex items-center gap-2 mb-6">
          {(['email', 'otp', 'success'] as Step[]).map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
                ${step === s || (i === 2 && step === 'success') ? 'bg-blue-600 text-white' :
                  (i < (['email','otp','success'] as Step[]).indexOf(step)) ? 'bg-emerald-500 text-white' : 'bg-gray-200 text-gray-500'}`}>
                {i + 1}
              </div>
              {i < 2 && <div className="flex-1 h-0.5 bg-gray-200 w-8" />}
            </div>
          ))}
          <span className="text-sm text-gray-500 ml-2">
            {step === 'email' ? 'Enter email' : step === 'otp' ? 'Enter OTP' : 'Done'}
          </span>
        </div>

        {step === 'email' && (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            <div>
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={handleResetPassword} className="space-y-4">
            {otpDebug && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm">
                <p className="font-semibold text-amber-800">Demo OTP (console log):</p>
                <p className="text-amber-900 font-mono text-lg tracking-widest mt-1">{otpDebug}</p>
              </div>
            )}
            <div>
              <label className="form-label">6-Digit OTP</label>
              <input
                type="text"
                className="form-input font-mono tracking-widest"
                value={otp}
                onChange={e => setOtp(e.target.value)}
                required
                maxLength={6}
                placeholder="000000"
              />
            </div>
            <div>
              <label className="form-label">New Password</label>
              <input
                type="password"
                className="form-input"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                required
                minLength={6}
                placeholder="••••••••"
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        {step === 'success' && (
          <div className="text-center py-4">
            <div className="text-5xl mb-4">✅</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Password Reset!</h3>
            <p className="text-gray-500 text-sm mb-6">You can now log in with your new password.</p>
            <Link to="/login" className="btn-primary inline-flex items-center gap-2">
              <ArrowLeft size={16} />
              Back to Login
            </Link>
          </div>
        )}

        {step !== 'success' && (
          <div className="mt-4 text-center">
            <Link to="/login" className="text-sm text-gray-500 hover:text-gray-700 flex items-center justify-center gap-1">
              <ArrowLeft size={14} />
              Back to login
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
