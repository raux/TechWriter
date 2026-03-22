import React, { useState } from 'react'
import './Sidebar.css'

function getSectionIcon(name) {
  if (name.includes('introduction')) return '📝'
  if (name.includes('rq')) return '❓'
  if (name.includes('methodology')) return '🔬'
  if (name.includes('results')) return '📊'
  if (name.includes('discussion')) return '💬'
  if (name.includes('conclusion')) return '🎯'
  if (name.includes('glossary')) return '📚'
  if (name.includes('related')) return '🔗'
  if (name.includes('data')) return '💾'
  return '📄'
}

export default function Sidebar({
  projects, currentProject, sections, selectedSection,
  onSelectProject, onCreateProject, onSelectSection
}) {
  const [newProjectName, setNewProjectName] = useState('')
  const [showNewProject, setShowNewProject] = useState(false)

  const handleCreate = () => {
    if (newProjectName.trim()) {
      onCreateProject(newProjectName.trim())
      setNewProjectName('')
      setShowNewProject(false)
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-header">
          <span>Projects</span>
          <button className="icon-btn" onClick={() => setShowNewProject(!showNewProject)} title="New project">+</button>
        </div>
        {showNewProject && (
          <div className="new-project-form">
            <input
              value={newProjectName}
              onChange={e => setNewProjectName(e.target.value)}
              placeholder="Project name"
              onKeyDown={e => e.key === 'Enter' && handleCreate()}
              autoFocus
            />
            <button onClick={handleCreate} className="btn btn-primary" style={{ padding: '4px 10px', fontSize: '0.8rem' }}>Create</button>
          </div>
        )}
        <ul className="project-list">
          {projects.map(p => (
            <li
              key={p}
              className={`project-item ${p === currentProject ? 'active' : ''}`}
              onClick={() => onSelectProject(p)}
            >
              📁 {p}
            </li>
          ))}
          {projects.length === 0 && <li className="empty-list">No projects yet</li>}
        </ul>
      </div>

      {currentProject && (
        <div className="sidebar-section sections-section">
          <div className="sidebar-header">
            <span>Sections ({sections.length})</span>
          </div>
          <ul className="section-list">
            {sections.map(s => (
              <li
                key={s}
                className={`section-item ${s === selectedSection ? 'active' : ''}`}
                onClick={() => onSelectSection(s)}
              >
                <span className="section-icon">{getSectionIcon(s)}</span>
                <span className="section-name">{s}</span>
              </li>
            ))}
            {sections.length === 0 && <li className="empty-list">No sections yet. Generate one!</li>}
          </ul>
        </div>
      )}
    </aside>
  )
}
