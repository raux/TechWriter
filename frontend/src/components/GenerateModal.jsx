import React, { useState } from 'react'
import './GenerateModal.css'

const SECTION_TYPES = [
  { value: 'introduction', label: '📝 Introduction' },
  { value: 'data_preparation', label: '💾 Data Preparation' },
  { value: 'rqs', label: '❓ Research Questions (RQs)' },
  { value: 'methodology', label: '🔬 Methodology' },
  { value: 'results', label: '📊 Results' },
  { value: 'discussion', label: '💬 Discussion' },
  { value: 'related_work', label: '🔗 Related Work' },
  { value: 'conclusion', label: '🎯 Conclusion' },
  { value: 'glossary', label: '📚 Glossary' },
]

export default function GenerateModal({ onGenerate, onClose }) {
  const [sectionType, setSectionType] = useState('introduction')
  const [sectionName, setSectionName] = useState('')
  const [additionalContext, setAdditionalContext] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const name = sectionName.trim() || sectionType
    onGenerate({ sectionType, sectionName: name, additionalContext })
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Generate Section</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label>Section Type</label>
            <select value={sectionType} onChange={e => setSectionType(e.target.value)}>
              {SECTION_TYPES.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Section Name <span className="optional">(optional, defaults to type)</span></label>
            <input
              type="text"
              value={sectionName}
              onChange={e => setSectionName(e.target.value)}
              placeholder="e.g. methodology_rq1, results_rq2"
            />
          </div>
          <div className="form-group">
            <label>Additional Context <span className="optional">(optional)</span></label>
            <textarea
              value={additionalContext}
              onChange={e => setAdditionalContext(e.target.value)}
              placeholder="Any specific instructions for the LLM..."
              rows={3}
            />
          </div>
          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Generate</button>
          </div>
        </form>
      </div>
    </div>
  )
}
