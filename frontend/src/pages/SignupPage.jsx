import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Wallet, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export const SignupPage = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  // Password constraint rules
  const hasMinLength = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>_\-+=\[\]]/.test(password);

  const isValidPassword = hasMinLength && hasUpper && hasLower && hasNumber && hasSpecial;
  const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!isValidEmail) {
      setError('Please enter a valid email address.');
      return;
    }

    if (!isValidPassword) {
      setError('Password does not meet all required security constraints.');
      return;
    }

    setIsSubmitting(true);
    try {
      await signup(email.trim().toLowerCase(), password, fullName.trim());
      navigate('/dashboard');
    } catch (err) {
      console.error('Signup error:', err);
      // Fallback for static demo environments (like GitHub Pages) when backend is offline
      if (!err.response) {
        console.warn('Backend server unreachable. Enabling offline demo access.');
        const mockUser = { id: 1, email: email.trim().toLowerCase(), full_name: fullName.trim() || 'Demo User' };
        localStorage.setItem('coinsy_token', 'demo-token');
        localStorage.setItem('coinsy_user', JSON.stringify(mockUser));
        window.location.href = '/dashboard';
        return;
      }

      const msg = err.response?.data?.detail;
      if (Array.isArray(msg)) {
        setError(msg.map((m) => m.msg).join(', '));
      } else {
        setError(msg || 'Failed to create account. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-slate-200 p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex bg-indigo-600 text-white p-3 rounded-xl mb-2">
            <Wallet className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Create your Coinsy Account</h1>
          <p className="text-sm text-slate-500">Track spending, insights & forecasts</p>
        </div>

        {error && (
          <div className="flex items-center space-x-2 bg-rose-50 border border-rose-200 text-rose-700 text-sm p-3 rounded-lg">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Full Name
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Karunya Kalkhundiya"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className={`w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 ${
                email && !isValidEmail ? 'border-rose-400 focus:ring-rose-400' : 'border-slate-300 focus:ring-indigo-500'
              }`}
            />
            {email && !isValidEmail && (
              <p className="text-[11px] text-rose-600 mt-1">Must be a valid email (e.g. name@domain.com)</p>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            {/* Password Security Rules Checklist */}
            <div className="mt-2.5 p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1">
              <div className="text-[11px] font-bold text-slate-700 mb-1">Password Requirements:</div>
              <div className="grid grid-cols-2 gap-1.5 text-[11px]">
                <span className={`flex items-center ${hasMinLength ? 'text-emerald-700 font-semibold' : 'text-slate-500'}`}>
                  {hasMinLength ? <CheckCircle className="w-3 h-3 mr-1 text-emerald-600" /> : <XCircle className="w-3 h-3 mr-1 text-slate-400" />}
                  Min 8 characters
                </span>
                <span className={`flex items-center ${hasUpper ? 'text-emerald-700 font-semibold' : 'text-slate-500'}`}>
                  {hasUpper ? <CheckCircle className="w-3 h-3 mr-1 text-emerald-600" /> : <XCircle className="w-3 h-3 mr-1 text-slate-400" />}
                  Uppercase (A-Z)
                </span>
                <span className={`flex items-center ${hasLower ? 'text-emerald-700 font-semibold' : 'text-slate-500'}`}>
                  {hasLower ? <CheckCircle className="w-3 h-3 mr-1 text-emerald-600" /> : <XCircle className="w-3 h-3 mr-1 text-slate-400" />}
                  Lowercase (a-z)
                </span>
                <span className={`flex items-center ${hasNumber ? 'text-emerald-700 font-semibold' : 'text-slate-500'}`}>
                  {hasNumber ? <CheckCircle className="w-3 h-3 mr-1 text-emerald-600" /> : <XCircle className="w-3 h-3 mr-1 text-slate-400" />}
                  Number (0-9)
                </span>
                <span className={`flex items-center col-span-2 ${hasSpecial ? 'text-emerald-700 font-semibold' : 'text-slate-500'}`}>
                  {hasSpecial ? <CheckCircle className="w-3 h-3 mr-1 text-emerald-600" /> : <XCircle className="w-3 h-3 mr-1 text-slate-400" />}
                  Special character (!@#$%^&*)
                </span>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !isValidPassword || !isValidEmail}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {isSubmitting ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="text-center text-sm text-slate-500 pt-2">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-600 font-medium hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
