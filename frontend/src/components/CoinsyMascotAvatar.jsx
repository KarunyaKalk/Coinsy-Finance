import React, { useEffect, useRef, useState } from 'react';

export const CoinsyMascotAvatar = ({
  mood = 'idle',
  isWiggling = false,
  isWelcome = false,
  size = 56,
  onClick,
}) => {
  const avatarRef = useRef(null);
  const [pupilOffset, setPupilOffset] = useState({ x: 0, y: 0 });
  const [isBlinking, setIsBlinking] = useState(false);

  // Eye cursor tracking logic
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!avatarRef.current) return;
      const rect = avatarRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const deltaX = e.clientX - centerX;
      const deltaY = e.clientY - centerY;
      const angle = Math.atan2(deltaY, deltaX);
      const distance = Math.min(Math.hypot(deltaX, deltaY) / 20, 3.5); // max 3.5px offset

      setPupilOffset({
        x: Math.cos(angle) * distance,
        y: Math.sin(angle) * distance,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Periodic eye blinking logic
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 200);
    }, 4500);

    return () => clearInterval(blinkInterval);
  }, []);

  // Mood color maps
  const getGlowColor = (m) => {
    switch (m) {
      case 'concerned':
        return 'drop-shadow(0 0 10px rgba(239, 68, 68, 0.5))';
      case 'celebrating':
        return 'drop-shadow(0 0 12px rgba(168, 85, 247, 0.6))';
      case 'happy':
        return 'drop-shadow(0 0 10px rgba(16, 185, 129, 0.5))';
      case 'thinking':
        return 'drop-shadow(0 0 10px rgba(59, 130, 246, 0.5))';
      case 'sleepy':
        return 'drop-shadow(0 0 8px rgba(148, 163, 184, 0.4))';
      default:
        return 'drop-shadow(0 0 10px rgba(99, 102, 241, 0.5))';
    }
  };

  return (
    <div
      ref={avatarRef}
      onClick={onClick}
      style={{ width: size, height: size, filter: getGlowColor(mood) }}
      className={`relative cursor-pointer select-none transition-transform duration-300 ${
        isWiggling ? 'animate-bounce scale-110' : ''
      } ${isWelcome ? 'animate-pulse scale-105' : 'hover:scale-105'}`}
      title={`Coinsy - Mood: ${mood}`}
    >
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full overflow-visible"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Outer Gold Coin Base */}
        <circle cx="50" cy="50" r="45" fill="url(#coinGradient)" stroke="#F59E0B" strokeWidth="3" />
        <circle cx="50" cy="50" r="38" stroke="#FCD34D" strokeWidth="1.5" strokeDasharray="4 2" />

        {/* Gradients */}
        <defs>
          <linearGradient id="coinGradient" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FBBF24" />
            <stop offset="50%" stopColor="#F59E0B" />
            <stop offset="100%" stopColor="#D97706" />
          </linearGradient>
        </defs>

        {/* Floating Mood Accessories */}
        {mood === 'celebrating' && (
          <g className="animate-bounce">
            {/* Party Hat */}
            <polygon points="50,4 36,24 64,24" fill="#EC4899" />
            <circle cx="50" cy="4" r="3.5" fill="#FDE047" />
            {/* Confetti */}
            <circle cx="20" cy="18" r="2" fill="#3B82F6" />
            <circle cx="80" cy="20" r="2.5" fill="#10B981" />
            <circle cx="75" cy="10" r="2" fill="#EC4899" />
          </g>
        )}

        {mood === 'thinking' && (
          <g className="animate-pulse">
            <circle cx="78" cy="22" r="3" fill="#60A5FA" />
            <circle cx="85" cy="15" r="4.5" fill="#3B82F6" />
            <circle cx="92" cy="7" r="6" fill="#2563EB" />
          </g>
        )}

        {mood === 'concerned' && (
          <g>
            {/* Alert Exclamation Mark */}
            <circle cx="80" cy="18" r="7" fill="#EF4444" />
            <text x="80" y="22" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">!</text>
          </g>
        )}

        {mood === 'sleepy' && (
          <g className="animate-pulse">
            <text x="74" y="24" fill="#94A3B8" fontSize="11" fontWeight="bold">Z</text>
            <text x="84" y="16" fill="#64748B" fontSize="13" fontWeight="bold">z</text>
            <text x="92" y="8" fill="#475569" fontSize="15" fontWeight="bold">z</text>
          </g>
        )}

        {/* Eyes Rendering */}
        {isBlinking || mood === 'sleepy' ? (
          /* Closed Eyes */
          <g stroke="#78350F" strokeWidth="3" strokeLinecap="round">
            <path d="M 33 42 Q 40 47 47 42" />
            <path d="M 53 42 Q 60 47 67 42" />
          </g>
        ) : (
          /* Open Eyes with Cursor Tracking */
          <g>
            {/* Left Eye */}
            <circle cx="40" cy="40" r="7.5" fill="white" />
            <circle
              cx={40 + pupilOffset.x}
              cy={40 + pupilOffset.y}
              r="3.5"
              fill="#451A03"
            />
            <circle
              cx={38.5 + pupilOffset.x}
              cy={38.5 + pupilOffset.y}
              r="1.2"
              fill="white"
            />

            {/* Right Eye */}
            <circle cx="60" cy="40" r="7.5" fill="white" />
            <circle
              cx={60 + pupilOffset.x}
              cy={40 + pupilOffset.y}
              r="3.5"
              fill="#451A03"
            />
            <circle
              cx={58.5 + pupilOffset.x}
              cy={38.5 + pupilOffset.y}
              r="1.2"
              fill="white"
            />

            {/* Concerned Eyebrows */}
            {mood === 'concerned' && (
              <g stroke="#78350F" strokeWidth="2.5" strokeLinecap="round">
                <line x1="32" y1="30" x2="45" y2="34" />
                <line x1="68" y1="30" x2="55" y2="34" />
              </g>
            )}
          </g>
        )}

        {/* Mouth Expressions */}
        {mood === 'happy' || mood === 'celebrating' ? (
          <path d="M 35 56 Q 50 72 65 56" fill="#78350F" stroke="#78350F" strokeWidth="2" />
        ) : mood === 'concerned' ? (
          <path d="M 36 62 Q 50 52 64 62" fill="none" stroke="#78350F" strokeWidth="3" strokeLinecap="round" />
        ) : mood === 'thinking' ? (
          <circle cx="50" cy="60" r="4" fill="#78350F" />
        ) : mood === 'sleepy' ? (
          <ellipse cx="50" cy="60" rx="3" ry="5" fill="#78350F" />
        ) : (
          /* Idle Smile */
          <path d="M 38 58 Q 50 67 62 58" fill="none" stroke="#78350F" strokeWidth="3" strokeLinecap="round" />
        )}

        {/* Cheeks */}
        <circle cx="30" cy="48" r="4" fill="#F43F5E" opacity="0.3" />
        <circle cx="70" cy="48" r="4" fill="#F43F5E" opacity="0.3" />
      </svg>
    </div>
  );
};

export default CoinsyMascotAvatar;
