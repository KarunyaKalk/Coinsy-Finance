import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { statementsApi } from '../api/client';
import { FileUp, FileText, CheckCircle2, AlertCircle, Lock, ShieldCheck, Info } from 'lucide-react';

export const ImportPage = () => {
  const { user } = useAuth();
  const [fileType, setFileType] = useState('csv'); // csv | pdf
  const [file, setFile] = useState(null);
  const [pdfPassword, setPdfPassword] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Privacy consent state
  const [hasConsented, setHasConsented] = useState(() => {
    return localStorage.getItem('coinsy_import_consent') === 'true';
  });
  const [showConsentModal, setShowConsentModal] = useState(!hasConsented);
  const [consentChecked, setConsentChecked] = useState(false);

  const handleAcceptConsent = () => {
    setHasConsented(true);
    localStorage.setItem('coinsy_import_consent', 'true');
    setShowConsentModal(false);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError('');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!hasConsented) {
      setShowConsentModal(true);
      return;
    }

    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setIsUploading(true);
    setError('');
    setResult(null);

    try {
      let res;
      if (fileType === 'csv') {
        res = await statementsApi.uploadCSV(file, user.id);
      } else {
        res = await statementsApi.uploadPDF(file, pdfPassword, user.id);
      }
      setResult(res);
      setFile(null);
      setPdfPassword('');
    } catch (err) {
      console.error('Import upload error:', err);
      const msg = err.response?.data?.detail || 'Failed to parse statement. Please verify file format.';
      setError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* First-Import Privacy Consent Modal */}
      {showConsentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-2xl shadow-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center space-x-3 text-indigo-600 border-b border-slate-100 pb-3">
              <ShieldCheck className="w-6 h-6 shrink-0" />
              <h2 className="text-lg font-bold text-slate-900">Data Privacy & Statement Processing Consent</h2>
            </div>

            <div className="space-y-3 text-xs text-slate-600 leading-relaxed max-h-60 overflow-y-auto pr-1">
              <p>
                Before uploading your bank statement, please review how Coinsy Finance handles your financial data:
              </p>

              <div className="bg-indigo-50 border border-indigo-100 p-3 rounded-xl space-y-1.5 text-indigo-950">
                <div className="font-semibold flex items-center space-x-1">
                  <Info className="w-3.5 h-3.5 text-indigo-600" />
                  <span>What is processed & stored:</span>
                </div>
                <ul className="list-disc pl-4 space-y-1">
                  <li><strong>Account Redaction:</strong> All 10-18 digit account numbers and 16-digit card numbers are automatically masked (e.g. XXXX-1234) before storage.</li>
                  <li><strong>Local Statement Parsing:</strong> CSV & PDF files are parsed locally into structured dates, descriptions, and amounts.</li>
                  <li><strong>AI Categorization:</strong> Clean transaction descriptions are categorized using secure batched AI prompts into default categories (Food, Transport, Rent, etc.).</li>
                  <li><strong>Data Ownership:</strong> Your transaction data belongs solely to you and is used exclusively for your personal budget dashboard and companion insights.</li>
                </ul>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 space-y-3">
              <label className="flex items-start space-x-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consentChecked}
                  onChange={(e) => setConsentChecked(e.target.checked)}
                  className="mt-0.5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-xs text-slate-700 font-medium">
                  I understand and consent to statement parsing, account number masking, and AI expense categorization.
                </span>
              </label>

              <button
                onClick={handleAcceptConsent}
                disabled={!consentChecked}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
              >
                I Agree & Continue to Upload
              </button>
            </div>
          </div>
        </div>
      )}

      <div>
        <h1 className="text-2xl font-bold text-slate-900">Import Bank Statement</h1>
        <p className="text-sm text-slate-500">
          Upload your bank statement in CSV or PDF format for automatic AI categorization.
        </p>
      </div>

      {/* Upload Box */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-6">
        {/* Privacy Info Banner */}
        <div className="flex items-center justify-between bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-lg text-xs text-slate-600">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Account numbers auto-redacted • Secure local statement parsing</span>
          </div>
          <button
            onClick={() => setShowConsentModal(true)}
            className="text-indigo-600 hover:underline font-medium ml-2"
          >
            Review Consent
          </button>
        </div>

        {/* Type Selector Tabs */}
        <div className="flex border-b border-slate-200">
          <button
            onClick={() => setFileType('csv')}
            className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
              fileType === 'csv'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            CSV Statement
          </button>
          <button
            onClick={() => setFileType('pdf')}
            className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
              fileType === 'pdf'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            PDF Statement
          </button>
        </div>

        {error && (
          <div className="flex items-center space-x-2 bg-rose-50 border border-rose-200 text-rose-700 text-sm p-3 rounded-lg">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="flex items-start space-x-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm p-4 rounded-lg">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold block">Statement Imported Successfully!</span>
              <span>
                Processed {result.processed_count || result.total_parsed || 0} transactions.{' '}
                {result.auto_categorized_count != null && `${result.auto_categorized_count} auto-categorized by AI.`}
              </span>
            </div>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-indigo-400 transition-colors bg-slate-50">
            <input
              type="file"
              accept={fileType === 'csv' ? '.csv' : '.pdf'}
              onChange={handleFileChange}
              id="statement-file-input"
              className="hidden"
            />
            <label htmlFor="statement-file-input" className="cursor-pointer space-y-2 block">
              <div className="inline-flex bg-indigo-50 text-indigo-600 p-3 rounded-full">
                <FileUp className="w-6 h-6" />
              </div>
              <div className="text-sm font-medium text-slate-800">
                {file ? file.name : `Click to select your ${fileType.toUpperCase()} file`}
              </div>
              <p className="text-xs text-slate-400">Supported formats: {fileType.toUpperCase()} files up to 10MB</p>
            </label>
          </div>

          {fileType === 'pdf' && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1 flex items-center space-x-1">
                <Lock className="w-3.5 h-3.5" />
                <span>PDF Password (Optional)</span>
              </label>
              <input
                type="password"
                value={pdfPassword}
                onChange={(e) => setPdfPassword(e.target.value)}
                placeholder="Enter password if PDF is password-protected"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={!file || isUploading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>{isUploading ? 'Parsing & Categorizing...' : 'Upload & Categorize Statement'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ImportPage;
