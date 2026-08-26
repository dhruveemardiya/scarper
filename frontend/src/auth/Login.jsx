import React, { useState, useEffect, useRef } from 'react';
import {
  Lock,
  User,
  Eye,
  EyeOff,
  ShieldCheck,
  DatabaseZap,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Search,
  Activity,
  FileSpreadsheet,
  Sun,
  Moon
} from 'lucide-react';
import { authService } from './authService';
import ForgotPasswordModal from './ForgotPasswordModal';

export default function Login({
  onLoginSuccess,
  initialError = '',
  theme = 'dark',
  toggleTheme
}) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(initialError);
  const [successMsg, setSuccessMsg] = useState('');
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (initialError) {
      setErrorMsg(initialError);
    }
  }, [initialError]);

  const handleThemeToggle = () => {
    if (typeof toggleTheme === 'function') {
      toggleTheme();
    } else {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
    }
  };

  // High-performance dynamic Business Intelligence & Data Network Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Create interconnected data nodes
    const nodeCount = Math.min(Math.floor((width * height) / 18000), 55);
    const nodes = [];

    // Predefined hub points (representing business intelligence pipeline clusters)
    const hubs = [
      { x: width * 0.15, y: height * 0.25, label: 'Discovery Engine', color: '#06b6d4', size: 5 },
      { x: width * 0.2, y: height * 0.75, label: 'Extraction Pipeline', color: '#f97316', size: 5.5 },
      { x: width * 0.82, y: height * 0.22, label: 'Verification Matrix', color: '#3b82f6', size: 5 },
      { x: width * 0.85, y: height * 0.78, label: 'CSV Export Hub', color: '#10b981', size: 4.5 }
    ];

    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2.2 + 1.2,
        pulse: Math.random() * Math.PI * 2,
        color: i % 4 === 0 ? 'rgba(249, 115, 22,' : i % 3 === 0 ? 'rgba(6, 182, 212,' : 'rgba(59, 130, 246,'
      });
    }

    // Moving data packets along network paths
    const packets = [];
    for (let k = 0; k < 12; k++) {
      packets.push({
        from: Math.floor(Math.random() * nodes.length),
        to: Math.floor(Math.random() * nodes.length),
        progress: Math.random(),
        speed: 0.003 + Math.random() * 0.004,
        color: k % 2 === 0 ? '#f97316' : '#38bdf8'
      });
    }

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw subtle coordinate grid lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
      ctx.lineWidth = 1;
      const gridSize = 60;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw subtle grid crosshairs
      ctx.fillStyle = 'rgba(59, 130, 246, 0.15)';
      for (let x = gridSize * 2; x < width; x += gridSize * 2) {
        for (let y = gridSize * 2; y < height; y += gridSize * 2) {
          ctx.fillRect(x - 2, y - 0.5, 4, 1);
          ctx.fillRect(x - 0.5, y - 2, 1, 4);
        }
      }

      // Draw node connection network
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 150) {
            const alpha = (1 - dist / 150) * 0.22;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `rgba(59, 130, 246, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      // Move and render data packets along lines
      packets.forEach((pkt) => {
        pkt.progress += pkt.speed;
        if (pkt.progress >= 1) {
          pkt.progress = 0;
          pkt.from = Math.floor(Math.random() * nodes.length);
          pkt.to = Math.floor(Math.random() * nodes.length);
        }
        const n1 = nodes[pkt.from];
        const n2 = nodes[pkt.to];
        if (n1 && n2) {
          const px = n1.x + (n2.x - n1.x) * pkt.progress;
          const py = n1.y + (n2.y - n1.y) * pkt.progress;
          ctx.beginPath();
          ctx.arc(px, py, 2, 0, Math.PI * 2);
          ctx.fillStyle = pkt.color;
          ctx.shadowBlur = 6;
          ctx.shadowColor = pkt.color;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Update and draw nodes
      for (let i = 0; i < nodes.length; i++) {
        const p = nodes[i];
        p.x += p.vx;
        p.y += p.vy;
        p.pulse += 0.03;

        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        const pulseScale = 1 + Math.sin(p.pulse) * 0.2;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * pulseScale, 0, Math.PI * 2);
        ctx.fillStyle = `${p.color} 0.7)`;
        ctx.shadowBlur = 6;
        ctx.shadowColor = `${p.color} 0.6)`;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // Draw pipeline hubs with pulsing radar rings
      hubs.forEach((hub, idx) => {
        const hx = (idx === 0 ? width * 0.15 : idx === 1 ? width * 0.18 : idx === 2 ? width * 0.82 : width * 0.84);
        const hy = (idx === 0 ? height * 0.24 : idx === 1 ? height * 0.72 : idx === 2 ? height * 0.22 : height * 0.76);

        const ringSize = (Date.now() / 30 + idx * 300) % 60;
        const ringAlpha = Math.max(0, 1 - ringSize / 60) * 0.35;

        // Radar wave ring
        ctx.beginPath();
        ctx.arc(hx, hy, ringSize, 0, Math.PI * 2);
        ctx.strokeStyle = hub.color;
        ctx.globalAlpha = ringAlpha;
        ctx.lineWidth = 1.2;
        ctx.stroke();
        ctx.globalAlpha = 1.0;

        // Core dot
        ctx.beginPath();
        ctx.arc(hx, hy, hub.size, 0, Math.PI * 2);
        ctx.fillStyle = hub.color;
        ctx.shadowBlur = 10;
        ctx.shadowColor = hub.color;
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    // Client-side presence validation
    if (!username.trim()) {
      setErrorMsg('Please enter your username.');
      return;
    }
    if (!password) {
      setErrorMsg('Please enter your password.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await authService.login(username.trim(), password);
      if (res.success) {
        setSuccessMsg('Access granted. Initializing workspace...');
        setTimeout(() => {
          if (typeof onLoginSuccess === 'function') {
            onLoginSuccess(res.user);
          }
        }, 500);
      } else {
        setErrorMsg(res.error || 'Invalid username or password.');
      }
    } catch (err) {
      setErrorMsg('Authentication error. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordResetSuccess = (msg) => {
    setSuccessMsg(msg || 'Password changed successfully. Please login with your new password.');
    setErrorMsg('');
  };

  return (
    <div className="login-container">
      {/* Dynamic Background Network & Business Intelligence Matrix */}
      <div className="login-bg-layer" aria-hidden="true">
        {/* Dynamic Vector/Plexus Network Canvas */}
        <canvas ref={canvasRef} className="login-network-canvas" />

        {/* Ambient atmospheric glow spots */}
        <div className="login-ambient-orb orb-primary" />
        <div className="login-ambient-orb orb-cyan" />
        <div className="login-ambient-orb orb-accent" />

        {/* Floating Side Info Cards: Discover → Extract → Verify → Export */}
        
        {/* 1. Top Left: Business Discovery */}
        <div className="hud-location-pin pin-left-top">
          <div className="pin-pulse-wrapper">
            <span className="pin-pulse-wave" />
            <Search size={14} className="pin-icon text-cyan" />
          </div>
          <div className="pin-content">
            <div className="pin-header">
              <span className="pin-title">Business Discovery</span>
              <span className="pin-badge">LIVE SEARCH</span>
            </div>
            <div className="pin-sub">
              <span>Search • Discover • Collect</span>
            </div>
          </div>
        </div>

        {/* 2. Bottom Left: Smart Data Extraction */}
        <div className="hud-location-pin pin-left-bottom">
          <div className="pin-pulse-wrapper">
            <span className="pin-pulse-wave orange-wave" />
            <Activity size={14} className="pin-icon text-orange" />
          </div>
          <div className="pin-content">
            <div className="pin-header">
              <span className="pin-title">Smart Data Extraction</span>
              <span className="pin-badge-live">LIVE SCRAPE</span>
            </div>
            <div className="pin-sub">
              <span>Contact • Address • Rating</span>
            </div>
          </div>
        </div>

        {/* 3. Top Right: Verified Business Data */}
        <div className="hud-location-pin pin-right-top">
          <div className="pin-pulse-wrapper">
            <span className="pin-pulse-wave blue-wave" />
            <ShieldCheck size={14} className="pin-icon text-blue" />
          </div>
          <div className="pin-content">
            <div className="pin-header">
              <span className="pin-title">Verified Business Data</span>
              <span className="pin-badge-blue">VERIFIED</span>
            </div>
            <div className="pin-sub">
              <span>Deduplicated • Verified</span>
            </div>
          </div>
        </div>

        {/* 4. Bottom Right: CSV Data Export */}
        <div className="hud-location-pin pin-right-bottom">
          <div className="pin-pulse-wrapper">
            <span className="pin-pulse-wave emerald-wave" />
            <FileSpreadsheet size={14} className="pin-icon text-emerald" />
          </div>
          <div className="pin-content">
            <div className="pin-header">
              <span className="pin-title">CSV Data Export</span>
              <span className="pin-badge-green">CSV EXPORT</span>
            </div>
            <div className="pin-sub">
              <span>Clean • Structured • Ready</span>
            </div>
          </div>
        </div>
      </div>

      {/* Prominently Centered Login Card */}
      <div className="login-center-wrapper">
        <div className="login-card">
          {/* Card Top-Right Theme Toggle Button */}
          <button
            type="button"
            className="btn-theme-toggle login-card-theme-toggle"
            onClick={handleThemeToggle}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle light and dark theme"
          >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          </button>

          {/* Header Branding */}
          <div className="login-card-header">
            <div className="login-brand-badge">
              <DatabaseZap size={30} />
            </div>
            <h1 className="login-title">DataScraper Desktop</h1>
            <p className="login-subtitle">
              Intelligent Business Data Extraction
            </p>

            <div className="login-tagline-pills">
              <span>Search</span>
              <span className="dot">•</span>
              <span>Scrape</span>
              <span className="dot">•</span>
              <span>Verify</span>
              <span className="dot">•</span>
              <span>Export</span>
            </div>

            <div className="security-shield-badge">
              <ShieldCheck size={15} />
              <span>Authorized Access Gateway</span>
            </div>
          </div>

          {/* Validation & Alert Messages */}
          {errorMsg && (
            <div className="auth-alert auth-alert-error" role="alert">
              <AlertCircle size={17} className="auth-alert-icon" />
              <div className="auth-alert-content">
                <span>{errorMsg}</span>
              </div>
            </div>
          )}

          {successMsg && (
            <div className="auth-alert auth-alert-success" role="status">
              <CheckCircle2 size={17} className="auth-alert-icon" />
              <div className="auth-alert-content">
                <span>{successMsg}</span>
              </div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="login-form">
            <div className="auth-form-group">
              <label htmlFor="login-username" className="auth-label">
                Username
              </label>
              <div className="auth-input-wrapper">
                <User size={18} className="auth-field-icon" />
                <input
                  id="login-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter username (e.g. Admin)"
                  className="auth-input auth-input-with-icon"
                  autoComplete="username"
                  autoFocus
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="auth-form-group">
              <label htmlFor="login-password" className="auth-label">
                Password
              </label>
              <div className="auth-input-wrapper">
                <Lock size={18} className="auth-field-icon" />
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  className="auth-input auth-input-with-icon"
                  autoComplete="current-password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? 'Hide password' : 'Show password'}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>

              {/* Forgot Password Button - directly under password field */}
              <div className="auth-forgot-row">
                <button
                  type="button"
                  className="auth-link-forgot"
                  onClick={() => setIsForgotModalOpen(true)}
                  tabIndex={0}
                >
                  Forgot Password?
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="login-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="auth-spinner" />
                  <span>Authenticating Access...</span>
                </>
              ) : (
                <>
                  <span>Sign In to Workspace</span>
                  <Sparkles size={16} />
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Forgot Password PIN Verification & Reset Modal */}
      <ForgotPasswordModal
        isOpen={isForgotModalOpen}
        onClose={() => setIsForgotModalOpen(false)}
        onSuccess={handlePasswordResetSuccess}
      />
    </div>
  );
}
