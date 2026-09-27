import React, { useState, useEffect } from 'react';
import { BrainCircuit, Sliders, ShieldCheck, AlertTriangle, Activity, Zap } from 'lucide-react';
import { adminApi } from '../api/adminApi';

export const AIRiskAnalytics = () => {
  const [factors, setFactors] = useState({
    crime_rate: 0.35,
    lighting_quality: 0.70,
    isolation_index: 0.25,
    crowd_density: 0.60,
    hour_of_day: 22
  });

  const [evaluation, setEvaluation] = useState({
    risk_score: 32.5,
    safety_score: 67.5,
    risk_category: 'LOW_SAFE',
    components: {
      crime_impact: 35.0,
      lighting_deficiency: 30.0,
      isolation_impact: 25.0,
      diurnal_vulnerability: 'NIGHT_HOURS'
    }
  });

  const [loading, setLoading] = useState(false);

  const runInference = async () => {
    setLoading(true);
    try {
      const res = await adminApi.evaluateRisk(factors);
      if (res.success) {
        setEvaluation(res.evaluation);
      }
    } catch (e) {
      console.warn('Risk inference error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(runInference, 200);
    return () => clearTimeout(timer);
  }, [factors]);

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">ANFIS Neuro-Fuzzy Risk Inference Engine</h1>
          <p className="page-desc">Interactive soft computing laboratory evaluating non-linear spatial safety risks</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px' }}>
        {/* Input Parameters Sliders */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sliders size={18} color="#002350" />
              <h3 className="card-title">Sensory & Contextual Inputs</h3>
            </div>
            <span className="badge badge-gold">MAMDANI / SUGENO</span>
          </div>

          <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Lighting */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', fontWeight: '600', marginBottom: '6px' }}>
                <span>Street Lighting Quality</span>
                <span style={{ color: '#D2AE39' }}>{Math.round(factors.lighting_quality * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={factors.lighting_quality}
                onChange={(e) => setFactors({ ...factors, lighting_quality: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#64748B' }}>
                <span>Pitch Dark Alley</span>
                <span>Daylight / Floodlit</span>
              </div>
            </div>

            {/* Crowd Density */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', fontWeight: '600', marginBottom: '6px' }}>
                <span>Crowd Density & Active Foot Traffic</span>
                <span style={{ color: '#002350' }}>{Math.round(factors.crowd_density * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={factors.crowd_density}
                onChange={(e) => setFactors({ ...factors, crowd_density: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#64748B' }}>
                <span>Deserted</span>
                <span>Active Market / Hub</span>
              </div>
            </div>

            {/* Crime Rate */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', fontWeight: '600', marginBottom: '6px' }}>
                <span>Historical Crime Index</span>
                <span style={{ color: '#EF4444' }}>{Math.round(factors.crime_rate * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={factors.crime_rate}
                onChange={(e) => setFactors({ ...factors, crime_rate: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#64748B' }}>
                <span>Zero Incidents</span>
                <span>High Frequency Zone</span>
              </div>
            </div>

            {/* Isolation Index */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', fontWeight: '600', marginBottom: '6px' }}>
                <span>Isolation & Enclosure Index</span>
                <span style={{ color: '#F59E0B' }}>{Math.round(factors.isolation_index * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={factors.isolation_index}
                onChange={(e) => setFactors({ ...factors, isolation_index: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>

            {/* Hour of Day */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', fontWeight: '600', marginBottom: '6px' }}>
                <span>Time of Day (Diurnal Vulnerability)</span>
                <span style={{ color: '#002350' }}>{factors.hour_of_day}:00 hrs</span>
              </div>
              <input
                type="range"
                min="0"
                max="23"
                step="1"
                value={factors.hour_of_day}
                onChange={(e) => setFactors({ ...factors, hour_of_day: parseInt(e.target.value) })}
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#64748B' }}>
                <span>Midnight (00:00)</span>
                <span>Noon (12:00)</span>
                <span>Night (23:00)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Inference Output Gauges */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BrainCircuit size={18} color="#002350" />
              <h3 className="card-title">Defuzzified Output Metrics</h3>
            </div>
            <span className="badge badge-resolved">REAL-TIME INFERENCE</span>
          </div>

          <div style={{ padding: '28px', textAlign: 'center' }}>
            <div style={{
              width: '180px',
              height: '180px',
              borderRadius: '50%',
              margin: '0 auto 20px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              background: evaluation.risk_score > 60 ? 'radial-gradient(circle, #FEE2E2 0%, #FEF2F2 100%)' : 'radial-gradient(circle, #D1FAE5 0%, #ECFDF5 100%)',
              border: `6px solid ${evaluation.risk_score > 60 ? '#EF4444' : '#10B981'}`,
              boxShadow: '0 10px 25px rgba(0, 35, 80, 0.1)'
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748B', textTransform: 'uppercase' }}>
                Safety Score
              </div>
              <div style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '3rem',
                fontWeight: '800',
                color: evaluation.risk_score > 60 ? '#B91C1C' : '#065F46',
                lineHeight: 1
              }}>
                {evaluation.safety_score}%
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: '600', color: '#475569', marginTop: '4px' }}>
                Risk: {evaluation.risk_score}/100
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <span className={`badge ${
                evaluation.risk_category === 'CRITICAL' ? 'badge-emergency' :
                evaluation.risk_category === 'ELEVATED' ? 'badge-warning' : 'badge-resolved'
              }`} style={{ fontSize: '0.90rem', padding: '6px 16px' }}>
                {evaluation.risk_category} CLASSIFICATION
              </span>
            </div>

            {/* Component Contributions */}
            <div style={{
              background: '#F8FAFC',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'left',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '12px'
            }}>
              <div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Crime Factor</div>
                <div style={{ fontWeight: '700', color: '#002350' }}>{evaluation.components?.crime_impact}%</div>
              </div>
              <div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Lighting Deficiency</div>
                <div style={{ fontWeight: '700', color: '#002350' }}>{evaluation.components?.lighting_deficiency}%</div>
              </div>
              <div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Diurnal Phase</div>
                <div style={{ fontWeight: '700', color: '#002350' }}>{evaluation.components?.diurnal_vulnerability}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Spatial Isolation</div>
                <div style={{ fontWeight: '700', color: '#002350' }}>{evaluation.components?.isolation_impact}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
