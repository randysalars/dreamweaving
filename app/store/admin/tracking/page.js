'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

function formatNumber(value) {
  try {
    return new Intl.NumberFormat('en-US').format(Number(value) || 0);
  } catch {
    return String(value ?? '');
  }
}

function formatUsd(value) {
  const number = Number(value) || 0;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(number);
}

function truncate(value, max = 4000) {
  if (typeof value !== 'string') return value;
  if (value.length <= max) return value;
  return value.slice(0, max) + '…';
}

function safeJson(value) {
  try {
    return truncate(JSON.stringify(value, null, 2));
  } catch {
    return '[unserializable]';
  }
}

export default function DreamweaverTrackingAdminPage() {
  const [days, setDays] = useState(7);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [sessionLookup, setSessionLookup] = useState('');
  const [orderLookup, setOrderLookup] = useState('');
  const [sessionDetail, setSessionDetail] = useState(null);
  const [orderDetail, setOrderDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  const daysOptions = useMemo(() => [7, 14, 30, 90, 180, 365], []);

  const fetchSummary = async nextDays => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/api/admin/tracking/summary?days=${nextDays}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.message || data?.error || 'Failed to load summary');
      }
      setSummary(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchSession = async sessionId => {
    if (!sessionId) return;
    setDetailLoading(true);
    setDetailError('');
    setSessionDetail(null);
    try {
      const response = await fetch(
        `/api/admin/tracking/sessions/${encodeURIComponent(sessionId)}`
      );
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.message || data?.error || 'Failed to load session');
      }
      setSessionDetail(data);
    } catch (e) {
      setDetailError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setDetailLoading(false);
    }
  };

  const fetchOrder = async orderId => {
    if (!orderId) return;
    setDetailLoading(true);
    setDetailError('');
    setOrderDetail(null);
    try {
      const response = await fetch(
        `/api/admin/tracking/orders/${encodeURIComponent(orderId)}`
      );
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.message || data?.error || 'Failed to load order');
      }
      setOrderDetail(data);
    } catch (e) {
      setDetailError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary(days);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [days]);

  const stats = summary || {
    window_days: days,
    sessions: 0,
    events: 0,
    conversions: 0,
    revenue_usd: 0,
    top_sources: [],
    recent_orders: [],
    recent_fulfillments: [],
    recent_events: [],
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
      <div
        style={{
          background: 'hsl(var(--card))',
          padding: '1rem 2rem',
          borderBottom: '1px solid #e5e7eb',
          marginBottom: '1.5rem',
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Link
            href='/store/admin'
            style={{
              color: '#2563eb',
              textDecoration: 'none',
              fontSize: '0.9rem',
              marginBottom: '0.75rem',
              display: 'inline-block',
            }}
          >
            ← Back to Admin Dashboard
          </Link>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
                Dreamweaver Tracking
              </h1>
              <div style={{ marginTop: '0.25rem', color: '#6b7280' }}>
                First-party analytics + webhook revenue signals (dw_* tables)
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <label style={{ fontSize: '0.9rem', color: '#374151' }}>
                Window
              </label>
              <select
                value={days}
                onChange={e => setDays(Number(e.target.value))}
                style={{
                  padding: '0.4rem 0.6rem',
                  borderRadius: '0.5rem',
                  border: '1px solid #d1d5db',
                  background: 'white',
                }}
              >
                {daysOptions.map(d => (
                  <option key={d} value={d}>
                    Last {d} days
                  </option>
                ))}
              </select>
              <button
                onClick={() => fetchSummary(days)}
                style={{
                  padding: '0.4rem 0.75rem',
                  borderRadius: '0.5rem',
                  border: '1px solid #d1d5db',
                  background: 'white',
                  cursor: 'pointer',
                }}
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem' }}>
        {error ? (
          <div
            style={{
              background: '#fee2e2',
              border: '1px solid #fecaca',
              color: '#991b1b',
              padding: '0.75rem 1rem',
              borderRadius: '0.75rem',
              marginBottom: '1rem',
            }}
          >
            {error}
          </div>
        ) : null}

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1rem',
            marginBottom: '1.25rem',
          }}
        >
          <StatCard
            label='Sessions'
            value={loading ? '…' : formatNumber(stats.sessions)}
          />
          <StatCard
            label='Events'
            value={loading ? '…' : formatNumber(stats.events)}
          />
          <StatCard
            label='Conversions'
            value={loading ? '…' : formatNumber(stats.conversions)}
          />
          <StatCard
            label='Revenue (USD)'
            value={loading ? '…' : formatUsd(stats.revenue_usd)}
          />
        </div>

        <div
          style={{
            background: 'white',
            borderRadius: '0.75rem',
            border: '1px solid #e5e7eb',
            padding: '1rem',
            marginBottom: '1rem',
          }}
        >
          <h2 style={{ margin: 0, fontSize: '1.1rem' }}>Lookup</h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '0.75rem',
              marginTop: '0.75rem',
            }}
          >
            <div>
              <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                Session ID
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.35rem' }}>
                <input
                  value={sessionLookup}
                  onChange={e => setSessionLookup(e.target.value)}
                  placeholder='dw_session_id'
                  style={inputStyle}
                />
                <button
                  onClick={() => fetchSession(sessionLookup.trim())}
                  style={buttonStyle}
                  disabled={detailLoading}
                >
                  View
                </button>
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                Order ID
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.35rem' }}>
                <input
                  value={orderLookup}
                  onChange={e => setOrderLookup(e.target.value)}
                  placeholder='dw_order_uuid'
                  style={inputStyle}
                />
                <button
                  onClick={() => fetchOrder(orderLookup.trim())}
                  style={buttonStyle}
                  disabled={detailLoading}
                >
                  View
                </button>
              </div>
            </div>
          </div>

          {detailError ? (
            <div style={{ marginTop: '0.75rem', color: '#991b1b' }}>
              {detailError}
            </div>
          ) : null}

          {detailLoading ? (
            <div style={{ marginTop: '0.75rem', color: '#6b7280' }}>
              Loading…
            </div>
          ) : null}

          {sessionDetail?.session ? (
            <DetailPanel
              title={`Session ${sessionDetail.session.session_id}`}
              subtitle={`${sessionDetail.events?.length || 0} events, ${sessionDetail.orders?.length || 0} orders`}
            >
              <KeyValueGrid
                entries={[
                  ['first_seen', sessionDetail.session.first_seen],
                  ['last_seen', sessionDetail.session.last_seen],
                  ['landing_path', sessionDetail.session.landing_path],
                  ['referrer', sessionDetail.session.referrer],
                  ['utm_source', sessionDetail.session.utm_source],
                  ['utm_medium', sessionDetail.session.utm_medium],
                  ['utm_campaign', sessionDetail.session.utm_campaign],
                  ['utm_content', sessionDetail.session.utm_content],
                  ['utm_term', sessionDetail.session.utm_term],
                  ['gclid', sessionDetail.session.gclid],
                  ['fbclid', sessionDetail.session.fbclid],
                ]}
              />
              <div style={{ marginTop: '0.75rem' }}>
                <h3 style={{ margin: 0, fontSize: '1rem' }}>Recent Events</h3>
                <SimpleTable
                  columns={['ts', 'name']}
                  rows={(sessionDetail.events || []).map(e => [
                    e.ts,
                    e.name,
                  ])}
                />
              </div>
            </DetailPanel>
          ) : null}

          {orderDetail?.order ? (
            <DetailPanel
              title={`Order ${orderDetail.order.order_id}`}
              subtitle={`${orderDetail.events?.length || 0} events, ${orderDetail.fulfillments?.length || 0} fulfillments`}
            >
              <KeyValueGrid
                entries={[
                  ['status', orderDetail.order.status],
                  ['provider', orderDetail.order.provider],
                  ['provider_txn_id', orderDetail.order.provider_txn_id],
                  ['created_at', orderDetail.order.created_at],
                  ['updated_at', orderDetail.order.updated_at],
                  ['amount', orderDetail.order.amount],
                  ['currency', orderDetail.order.currency],
                  ['product_sku', orderDetail.order.product_sku],
                  ['session_id', orderDetail.order.session_id],
                ]}
              />
              <div style={{ marginTop: '0.75rem' }}>
                <h3 style={{ margin: 0, fontSize: '1rem' }}>Attribution</h3>
                <pre style={preStyle}>{safeJson(orderDetail.order.attrib)}</pre>
              </div>
            </DetailPanel>
          ) : null}
        </div>

        <TwoCol>
          <Panel title='Top Sources'>
            <SimpleTable
              columns={['utm_source', 'sessions']}
              rows={(stats.top_sources || []).map(r => [
                r.utm_source || '(direct)',
                formatNumber(r.sessions),
              ])}
            />
          </Panel>
          <Panel title='Recent Fulfillments'>
            <SimpleTable
              columns={['created_at', 'order_id', 'product_sku', 'delivered_at']}
              rows={(stats.recent_fulfillments || []).map(f => [
                f.created_at,
                f.order_id,
                f.product_sku || '',
                f.delivered_at || '',
              ])}
            />
          </Panel>
        </TwoCol>

        <Panel title='Recent Orders'>
          <SimpleTable
            columns={[
              'created_at',
              'order_id',
              'provider',
              'status',
              'amount',
              'product_sku',
              'session_id',
            ]}
            rows={(stats.recent_orders || []).map(o => [
              o.created_at,
              o.order_id,
              o.provider,
              o.status,
              o.amount ? `${o.amount} ${o.currency || ''}`.trim() : '',
              o.product_sku || '',
              o.session_id || '',
            ])}
            onRowClick={row => {
              const orderId = row?.[1];
              if (orderId) {
                setOrderLookup(orderId);
                fetchOrder(orderId);
              }
            }}
          />
          <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#6b7280' }}>
            Click a row to open order details.
          </div>
        </Panel>

        <Panel title='Recent Events'>
          <SimpleTable
            columns={['ts', 'session_id', 'name']}
            rows={(stats.recent_events || []).map(e => [
              e.ts,
              e.session_id || '',
              e.name,
            ])}
            onRowClick={row => {
              const sessionId = row?.[1];
              if (sessionId) {
                setSessionLookup(sessionId);
                fetchSession(sessionId);
              }
            }}
          />
          <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#6b7280' }}>
            Click a row to open session details.
          </div>
        </Panel>

        <div style={{ height: '2rem' }} />
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div
      style={{
        background: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '0.75rem',
        padding: '1rem',
      }}
    >
      <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>{label}</div>
      <div style={{ fontSize: '1.6rem', fontWeight: 700, marginTop: '0.3rem' }}>
        {value}
      </div>
    </div>
  );
}

function TwoCol({ children }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '1rem',
        marginBottom: '1rem',
      }}
    >
      {children}
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div
      style={{
        background: 'white',
        borderRadius: '0.75rem',
        border: '1px solid #e5e7eb',
        padding: '1rem',
        marginBottom: '1rem',
      }}
    >
      <h2 style={{ margin: 0, fontSize: '1.1rem' }}>{title}</h2>
      <div style={{ marginTop: '0.75rem' }}>{children}</div>
    </div>
  );
}

function DetailPanel({ title, subtitle, children }) {
  return (
    <div
      style={{
        marginTop: '1rem',
        paddingTop: '1rem',
        borderTop: '1px solid #e5e7eb',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <div style={{ fontSize: '1rem', fontWeight: 700 }}>{title}</div>
          <div style={{ marginTop: '0.15rem', color: '#6b7280', fontSize: '0.9rem' }}>
            {subtitle}
          </div>
        </div>
      </div>
      <div style={{ marginTop: '0.75rem' }}>{children}</div>
    </div>
  );
}

function KeyValueGrid({ entries }) {
  const filtered = (entries || []).filter(([_, v]) => v !== null && v !== undefined && v !== '');
  if (filtered.length === 0) return null;
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '0.5rem 1rem',
      }}
    >
      {filtered.map(([k, v]) => (
        <div key={k} style={{ fontSize: '0.9rem' }}>
          <span style={{ color: '#6b7280' }}>{k}</span>
          <div style={{ fontWeight: 600, wordBreak: 'break-word' }}>
            {String(v)}
          </div>
        </div>
      ))}
    </div>
  );
}

function SimpleTable({ columns, rows, onRowClick }) {
  const hasRows = rows && rows.length > 0;
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {columns.map(col => (
              <th
                key={col}
                style={{
                  textAlign: 'left',
                  fontSize: '0.85rem',
                  color: '#6b7280',
                  padding: '0.5rem 0.5rem',
                  borderBottom: '1px solid #e5e7eb',
                  whiteSpace: 'nowrap',
                }}
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {hasRows
            ? rows.map((row, idx) => (
                <tr
                  key={idx}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  style={{
                    cursor: onRowClick ? 'pointer' : 'default',
                    background: idx % 2 === 0 ? 'white' : '#fafafa',
                  }}
                >
                  {row.map((cell, cIdx) => (
                    <td
                      key={cIdx}
                      style={{
                        padding: '0.45rem 0.5rem',
                        borderBottom: '1px solid #f3f4f6',
                        fontSize: '0.9rem',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {String(cell ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            : (
              <tr>
                <td
                  colSpan={columns.length}
                  style={{
                    padding: '0.75rem 0.5rem',
                    color: '#6b7280',
                    fontSize: '0.9rem',
                  }}
                >
                  No data.
                </td>
              </tr>
            )}
        </tbody>
      </table>
    </div>
  );
}

const inputStyle = {
  flex: 1,
  padding: '0.55rem 0.65rem',
  borderRadius: '0.5rem',
  border: '1px solid #d1d5db',
  background: 'white',
};

const buttonStyle = {
  padding: '0.55rem 0.85rem',
  borderRadius: '0.5rem',
  border: '1px solid #d1d5db',
  background: 'white',
  cursor: 'pointer',
};

const preStyle = {
  margin: '0.5rem 0 0 0',
  padding: '0.75rem',
  background: '#0b1020',
  color: '#e5e7eb',
  borderRadius: '0.75rem',
  overflowX: 'auto',
  fontSize: '0.85rem',
  lineHeight: 1.35,
};

