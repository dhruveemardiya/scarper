import React, { useEffect } from 'react';
import { Trash2, AlertTriangle, X, FileSpreadsheet, RotateCcw } from 'lucide-react';

export default function ConfirmDeleteModal({
  isOpen,
  record,
  file,
  isClearTable = false,
  onConfirm,
  onCancel,
  title,
  message,
  confirmText,
  cancelText = "Cancel"
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;
      if (e.key === 'Escape') {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  let modalTitle = title;
  let modalPrompt = '';
  let modalChip = null;
  let modalSubmessage = message;
  let btnConfirmText = confirmText;
  let confirmIcon = <Trash2 size={16} />;

  if (isClearTable) {
    modalTitle = modalTitle || "Clear Table View?";
    modalPrompt = "Clear all active records from the table view?";
    modalSubmessage = modalSubmessage || "The CSV files saved on your disk will remain completely safe and untouched.";
    btnConfirmText = btnConfirmText || "Yes, clear table";
    confirmIcon = <RotateCcw size={16} />;
  } else if (file) {
    modalTitle = modalTitle || "Delete CSV File?";
    modalPrompt = `Delete "${file.filename || file.filepath || 'this file'}" from disk?`;
    modalChip = (
      <div className="swal-record-chip">
        <FileSpreadsheet size={13} style={{ color: 'var(--accent)' }} />
        <span>{file.records_count !== undefined ? `${file.records_count} records` : 'CSV File'}</span>
        {file.size_formatted && <span>&bull;</span>}
        {file.size_formatted && <span>{file.size_formatted}</span>}
      </div>
    );
    modalSubmessage = modalSubmessage || "This file will be permanently deleted from your local storage.";
    btnConfirmText = btnConfirmText || "Yes, delete file";
  } else {
    const recordName = record?.name || record?.['Business Name'] || record?.['Hospital Name'] || record?.['School Name'] || 'this record';
    const category = record?.category || record?.Category || record?.entity_label || '';
    const pincode = record?.pincode || record?.Pincode || record?.search_pincode || '';

    modalTitle = modalTitle || "Delete Record?";
    modalPrompt = `Do you want to delete "${recordName}"?`;
    if (category || pincode) {
      modalChip = (
        <div className="swal-record-chip">
          {category && <span>{category}</span>}
          {category && pincode && <span>&bull;</span>}
          {pincode && <span>Postal Code: {pincode}</span>}
        </div>
      );
    }
    modalSubmessage = modalSubmessage || "This record will be removed from your active dataset view.";
    btnConfirmText = btnConfirmText || "Yes, delete it!";
  }

  return (
    <div className="modal-overlay swal-overlay" onClick={onCancel}>
      <div
        className="modal-content swal-modal-container"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {/* SweetAlert Animated Warning Icon */}
        <div className="swal-icon-wrapper">
          <div className="swal-warning-pulse"></div>
          <div className="swal-warning-circle">
            <span className="swal-exclamation-mark">!</span>
          </div>
        </div>

        {/* Title & Body */}
        <div className="swal-text-container">
          <h3 className="swal-title">{modalTitle}</h3>
          <p className="swal-message">
            {modalPrompt}
          </p>
          {modalChip}
          <p className="swal-submessage">{modalSubmessage}</p>
        </div>

        {/* Action Buttons */}
        <div className="swal-actions-row">
          <button
            type="button"
            className="btn btn-secondary swal-btn-cancel"
            onClick={onCancel}
          >
            {cancelText}
          </button>
          <button
            type="button"
            className="btn btn-danger swal-btn-confirm"
            onClick={() => onConfirm(record || file)}
            autoFocus
          >
            {confirmIcon}
            <span>{btnConfirmText}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
