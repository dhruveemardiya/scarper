import React, { useState } from 'react';
import { KeyRound, ShieldAlert, CheckCircle2, Lock, Eye, EyeOff, X, ArrowLeft, Loader2 } from 'lucide-react';
import { authService } from './authService';

export default function ForgotPasswordModal({ isOpen, onClose, onSuccess }) {
  const [step, setStep] = useState(1); // 1: Enter PIN, 2: Set New Password
  const [pin, setPin] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  if (!isOpen) return null;

  const handleClose = () => {
    setStep(1);
    setPin('');
    setResetToken('');
    setNewPassword('');
    setConfirmPassword('');
    setErrorMsg('');
    setSuccessMsg('');
    onClose();
  };

  const handleVerifyPin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!pin.trim()) {
      setErrorMsg('Please enter your security PIN.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await authService.verifyPin(pin.trim());
      if (res.success && res.resetToken) {
        setResetToken(res.resetToken);
        setStep(2);
        setErrorMsg('');
      } else {
        setErrorMsg(res.error || 'Invalid PIN');
      }
    } catch (err) {
      setErrorMsg('Failed to verify PIN. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!newPassword) {
      setErrorMsg('New password cannot be empty.');
      return;
    }
    if (newPassword.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setErrorMsg('New password and confirmation do not match.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await authService.resetPassword(resetToken, newPassword);
      if (res.success) {
        setSuccessMsg(res.message || 'Password changed successfully. Please login with your new password.');
        setTimeout(() => {
          handleClose();
          if (typeof onSuccess === 'function') {
            onSuccess(res.message || 'Password changed successfully. Please login with your new password.');
          }
        }, 1800);
      } else {
        setErrorMsg(res.error || 'Failed to update password.');
      }
    } catch (err) {
      setErrorMsg('Failed to update password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-modal-overlay" onClick={handleClose}>
      <div className="auth-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="auth-modal-header">
          <div className="auth-modal-title-row">
            <div className="auth-icon-badge">
              <KeyRound size={20} />
            </div>
            <div>
              <h3 className="auth-modal-title">
                {step === 1 ? 'Reset Password Authorization' : 'Set New Password'}
              </h3>
              <p className="auth-modal-subtitle">
                {step === 1 ? 'Enter your server-configured security PIN to verify identity' : 'Enter and confirm your new secure administrator password'}
              </p>
            </div>
          </div>
          <button type="button" className="auth-modal-close" onClick={handleClose}>
            <X size={18} />
          </button>
        </div>

        {errorMsg && (
          <div className="auth-alert auth-alert-error" role="alert">
            <ShieldAlert size={16} className="auth-alert-icon" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="auth-alert auth-alert-success" role="status">
            <CheckCircle2 size={16} className="auth-alert-icon" />
            <span>{successMsg}</span>
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleVerifyPin} className="auth-form-body">
            <div className="auth-form-group">
              <label htmlFor="security-pin" className="auth-label">
                Security PIN
              </label>
              <div className="auth-input-wrapper">
                <input
                  id="security-pin"
                  type="password"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  placeholder="Enter PIN"
                  className="auth-input"
                  autoFocus
                  maxLength={12}
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="auth-modal-actions">
              <button
                type="button"
                className="auth-btn-secondary"
                onClick={handleClose}
                disabled={isLoading}
              >
                <ArrowLeft size={16} />
                <span>Back to Login</span>
              </button>
              <button
                type="submit"
                className="auth-btn-primary"
                disabled={isLoading || !pin}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="auth-spinner" />
                    <span>Verifying...</span>
                  </>
                ) : (
                  <span>Verify PIN</span>
                )}
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleResetPassword} className="auth-form-body">
            <div className="auth-form-group">
              <label htmlFor="new-password" className="auth-label">
                New Password
              </label>
              <div className="auth-input-wrapper">
                <Lock size={18} className="auth-field-icon" />
                <input
                  id="new-password"
                  type={showPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password"
                  className="auth-input auth-input-with-icon"
                  autoFocus
                  disabled={isLoading || !!successMsg}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="auth-form-group">
              <label htmlFor="confirm-password" className="auth-label">
                Confirm New Password
              </label>
              <div className="auth-input-wrapper">
                <Lock size={18} className="auth-field-icon" />
                <input
                  id="confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password"
                  className="auth-input auth-input-with-icon"
                  disabled={isLoading || !!successMsg}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  tabIndex={-1}
                >
                  {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="auth-modal-actions">
              <button
                type="button"
                className="auth-btn-secondary"
                onClick={() => setStep(1)}
                disabled={isLoading || !!successMsg}
              >
                <ArrowLeft size={16} />
                <span>Back</span>
              </button>
              <button
                type="submit"
                className="auth-btn-primary"
                disabled={isLoading || !newPassword || !confirmPassword || !!successMsg}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="auth-spinner" />
                    <span>Updating...</span>
                  </>
                ) : (
                  <span>Set Password</span>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
