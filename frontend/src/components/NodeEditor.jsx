import React from 'react'
import './NodeEditor.css'

export default function NodeEditor({ sectionName, content, onContentChange, onSave, onValidate, validationResults, loading }) {
  return (
    <aside className="node-editor">
      <div className="editor-header">
        <h3 className="editor-title">{sectionName?.replace(/_/g, ' ')}</h3>
        <div className="editor-actions">
          <button onClick={onValidate} className="btn btn-secondary" disabled={loading}>
            {loading ? '…' : 'Validate'}
          </button>
          <button onClick={onSave} className="btn btn-primary">
            Save
          </button>
        </div>
      </div>

      <textarea
        className="editor-textarea"
        value={content}
        onChange={e => onContentChange(e.target.value)}
        placeholder="Section content (Markdown)..."
        spellCheck={false}
      />

      {validationResults && (
        <div className="validation-panel">
          <h4 className="validation-title">
            Validation Results
            <span className={`issue-count ${validationResults.issues.length === 0 ? 'ok' : 'warn'}`}>
              {validationResults.issues.length === 0 ? '✓ OK' : `${validationResults.issues.length} issue(s)`}
            </span>
          </h4>
          {validationResults.issues.length === 0 ? (
            <p className="no-issues">No issues found. Section aligns with RQs.</p>
          ) : (
            <ul className="issue-list">
              {validationResults.issues.map((issue, i) => (
                <li key={i} className="issue-item">{issue}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </aside>
  )
}
