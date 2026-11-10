import React, { useCallback, useEffect, useState } from 'react';
import { telemetryAPI } from '../services/api';

const CONSENT_KEY = 'ap1-analytics-consent';
const VIEW_KEY = 'ap1-analytics-page-view-recorded';

export const TelemetryPanel = () => {
  const [consent, setConsent] = useState(() => {
    try {
      return window.localStorage.getItem(CONSENT_KEY) || 'unset';
    } catch {
      return 'unset';
    }
  });
  const [publicStats, setPublicStats] = useState(null);
  const [adminOpen, setAdminOpen] = useState(false);
  const [adminToken, setAdminToken] = useState('');
  const [adminStats, setAdminStats] = useState(null);
  const [adminError, setAdminError] = useState('');
  const [loadingAdmin, setLoadingAdmin] = useState(false);

  const loadPublicStats = useCallback(async () => {
    try {
      const response = await telemetryAPI.getPublicSummary();
      if (response.success) setPublicStats(response.data);
    } catch {
      setPublicStats(null);
    }
  }, []);

  const recordPageView = useCallback(async () => {
    try {
      if (window.sessionStorage.getItem(VIEW_KEY) === '1') return;
      await telemetryAPI.recordEvent('page_view');
      window.sessionStorage.setItem(VIEW_KEY, '1');
      await loadPublicStats();
    } catch {
      // Telemetry must never interrupt the portfolio experience.
    }
  }, [loadPublicStats]);

  useEffect(() => {
    loadPublicStats();
    if (consent === 'accepted') recordPageView();
  }, [consent, loadPublicStats, recordPageView]);

  const chooseConsent = (choice) => {
    try {
      window.localStorage.setItem(CONSENT_KEY, choice);
    } catch {
      // If storage is unavailable, do not enable tracking for this visit.
    }
    setConsent(choice);
    if (choice === 'accepted') recordPageView();
  };

  const loadAdminStats = async () => {
    setLoadingAdmin(true);
    setAdminError('');
    setAdminStats(null);
    try {
      const response = await telemetryAPI.getAdminSummary(adminToken);
      if (response.success) setAdminStats(response.data);
      else setAdminError('Admin analytics could not be loaded.');
    } catch (error) {
      const status = error?.response?.status;
      setAdminError(
        status === 401
          ? 'Access denied. Check the admin token.'
          : status === 503
            ? 'Admin analytics is not configured on the server yet.'
            : 'Admin analytics is temporarily unavailable.'
      );
    } finally {
      setLoadingAdmin(false);
    }
  };

  return (
    <section aria-label="Website analytics" className="py-8 bg-slate-50 dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/70 p-5 md:p-7">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">AP1 Site Insights</h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">Privacy-respecting aggregate activity</p>
            </div>
            <span className="text-xs rounded-full px-3 py-1 bg-cyan-50 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-300">
              First-party analytics
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-50 dark:bg-slate-800/70 p-4">
              <p className="text-xs text-slate-500 dark:text-slate-400">All-time page views</p>
              <p className="text-2xl font-bold text-cyan-600 dark:text-cyan-400">
                {publicStats ? publicStats.page_views_all_time.toLocaleString() : '—'}
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 dark:bg-slate-800/70 p-4">
              <p className="text-xs text-slate-500 dark:text-slate-400">Last 7 days</p>
              <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">
                {publicStats ? publicStats.page_views_last_7_days.toLocaleString() : '—'}
              </p>
            </div>
          </div>

          {consent === 'unset' && (
            <div className="mt-4 rounded-xl border border-cyan-200 dark:border-cyan-900 p-4">
              <p className="text-sm text-slate-700 dark:text-slate-300">
                Allow anonymous page-view counting? Only daily totals are stored. No IP address,
                name, email, user-agent, referrer or fingerprint is collected.
              </p>
              <div className="flex flex-wrap gap-2 mt-3">
                <button type="button" onClick={() => chooseConsent('accepted')} className="rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-700">
                  Allow analytics
                </button>
                <button type="button" onClick={() => chooseConsent('declined')} className="rounded-lg border border-slate-300 dark:border-slate-700 px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
                  No thanks
                </button>
              </div>
            </div>
          )}

          {consent !== 'unset' && (
            <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Analytics consent: {consent === 'accepted' ? 'allowed' : 'declined'}.
              </p>
              <button type="button" onClick={() => chooseConsent(consent === 'accepted' ? 'declined' : 'accepted')} className="text-xs font-medium text-cyan-700 dark:text-cyan-400 underline">
                {consent === 'accepted' ? 'Opt out' : 'Change to allow'}
              </button>
            </div>
          )}

          <div className="mt-5 border-t border-slate-200 dark:border-slate-800 pt-4">
            <button type="button" onClick={() => setAdminOpen(value => !value)} className="text-sm font-semibold text-slate-700 dark:text-slate-300 hover:text-cyan-600">
              {adminOpen ? 'Hide admin analytics' : 'Owner / admin analytics'}
            </button>
            {adminOpen && (
              <div className="mt-3 space-y-3">
                <label htmlFor="ap1-admin-token" className="block text-xs text-slate-600 dark:text-slate-400">
                  Server-configured admin token (kept in memory only)
                </label>
                <div className="flex flex-col sm:flex-row gap-2">
                  <input
                    id="ap1-admin-token"
                    type="password"
                    autoComplete="off"
                    value={adminToken}
                    onChange={(event) => setAdminToken(event.target.value)}
                    placeholder="Enter admin token"
                    className="min-w-0 flex-1 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-sm text-slate-900 dark:text-white"
                  />
                  <button type="button" onClick={loadAdminStats} disabled={!adminToken || loadingAdmin} className="rounded-lg bg-slate-900 dark:bg-slate-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">
                    {loadingAdmin ? 'Checking…' : 'Open analytics'}
                  </button>
                </div>
                {adminError && <p role="alert" className="text-sm text-amber-700 dark:text-amber-400">{adminError}</p>}
                {adminStats && (
                  <div className="rounded-xl bg-slate-50 dark:bg-slate-800/70 p-4">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">
                      {adminStats.page_views_in_window.toLocaleString()} views in {adminStats.window_days} days
                    </p>
                    <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
                      {adminStats.daily.map((day) => (
                        <div key={day.day} className="flex justify-between gap-4 text-xs text-slate-600 dark:text-slate-300">
                          <span>{day.day}</span><span className="font-semibold">{day.page_views}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default TelemetryPanel;
