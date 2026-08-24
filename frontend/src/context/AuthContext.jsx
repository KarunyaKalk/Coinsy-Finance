import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('coinsy_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('coinsy_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('coinsy_token');
      if (storedToken) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
          localStorage.setItem('coinsy_user', JSON.stringify(userData));
        } catch (err) {
          console.error('Failed to validate auth token:', err);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const res = await authApi.login(email, password);
    setToken(res.access_token);
    setUser(res.user);
    localStorage.setItem('coinsy_token', res.access_token);
    localStorage.setItem('coinsy_user', JSON.stringify(res.user));
    return res.user;
  };

  const signup = async (email, password, fullName) => {
    const res = await authApi.signup(email, password, fullName);
    setToken(res.access_token);
    setUser(res.user);
    localStorage.setItem('coinsy_token', res.access_token);
    localStorage.setItem('coinsy_user', JSON.stringify(res.user));
    return res.user;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('coinsy_token');
    localStorage.removeItem('coinsy_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!token,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
