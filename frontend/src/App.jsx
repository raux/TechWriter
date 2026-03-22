import React, { useState, useEffect, useCallback } from 'react'
import Canvas from './components/Canvas.jsx'
import NodeEditor from './components/NodeEditor.jsx'
import Sidebar from './components/Sidebar.jsx'
import GenerateModal from './components/GenerateModal.jsx'
import {
  listProjects, createProject, listSections, getSection,
  updateSection, deleteSection, getCanvasMeta, generateSection,
  validateSection, checkConsistency, createSection
} from './services/api.js'
import './App.css'

const TOAST_DURATION_MS = 3000

export default function App() {
  const [projects, setProjects] = useState([])
  const [currentProject, setCurrentProject] = useState(null)
  const [sections, setSections] = useState([])
  const [canvasMeta, setCanvasMeta] = useState({ nodes: [] })
  const [selectedSection, setSelectedSection] = useState(null)
  const [sectionContent, setSectionContent] = useState('')
  const [validationResults, setValidationResults] = useState(null)
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), TOAST_DURATION_MS)
  }

  useEffect(() => {
    listProjects().then(r => setProjects(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    if (!currentProject) return
    Promise.all([listSections(currentProject), getCanvasMeta(currentProject)])
      .then(([secResp, canvasResp]) => {
        setSections(secResp.data)
        setCanvasMeta(canvasResp.data)
      })
      .catch(() => {})
  }, [currentProject])

  const handleSelectSection = async (sectionName) => {
    if (!currentProject) return
    setSelectedSection(sectionName)
    setValidationResults(null)
    try {
      const r = await getSection(currentProject, sectionName)
      setSectionContent(r.data.content)
    } catch {
      setSectionContent('')
    }
  }

  const handleSaveSection = async () => {
    if (!currentProject || !selectedSection) return
    try {
      await updateSection(currentProject, selectedSection, sectionContent)
      showToast('Section saved')
    } catch (e) {
      showToast('Failed to save section', 'error')
    }
  }

  const handleValidate = async () => {
    if (!currentProject || !selectedSection) return
    setLoading(true)
    try {
      const r = await validateSection(currentProject, selectedSection)
      setValidationResults(r.data)
      showToast(
        r.data.issues.length === 0 ? 'No issues found' : `${r.data.issues.length} issue(s) found`,
        r.data.issues.length === 0 ? 'success' : 'warning'
      )
    } catch {
      showToast('Validation failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleConsistencyCheck = async () => {
    if (!currentProject) return
    setLoading(true)
    try {
      const r = await checkConsistency(currentProject)
      showToast(
        `Consistency check: ${r.data.length} issue(s) found`,
        r.data.length === 0 ? 'success' : 'warning'
      )
    } catch {
      showToast('Consistency check failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async ({ sectionType, sectionName, additionalContext }) => {
    if (!currentProject) return
    setLoading(true)
    setShowGenerateModal(false)
    try {
      await generateSection(currentProject, sectionType, sectionName, additionalContext)
      const [secResp, canvasResp] = await Promise.all([
        listSections(currentProject),
        getCanvasMeta(currentProject),
      ])
      setSections(secResp.data)
      setCanvasMeta(canvasResp.data)
      await handleSelectSection(sectionName)
      showToast(`Section '${sectionName}' generated`)
    } catch {
      showToast('Generation failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async (name) => {
    try {
      await createProject(name)
      const r = await listProjects()
      setProjects(r.data)
      setCurrentProject(name)
      showToast(`Project '${name}' created`)
    } catch {
      showToast('Failed to create project', 'error')
    }
  }

  const handleNodeMove = (nodeId, x, y) => {
    setCanvasMeta(prev => ({
      ...prev,
      nodes: prev.nodes.map(n => n.id === nodeId ? { ...n, x, y } : n),
    }))
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>TechWriter</h1>
        <span className="app-subtitle">Academic Paper Canvas</span>
        {currentProject && (
          <div className="header-actions">
            <button onClick={() => setShowGenerateModal(true)} className="btn btn-primary">
              + Generate Section
            </button>
            <button onClick={handleConsistencyCheck} className="btn btn-secondary" disabled={loading}>
              Consistency Check
            </button>
          </div>
        )}
      </header>

      <div className="app-body">
        <Sidebar
          projects={projects}
          currentProject={currentProject}
          sections={sections}
          onSelectProject={setCurrentProject}
          onCreateProject={handleCreateProject}
          onSelectSection={handleSelectSection}
          selectedSection={selectedSection}
        />

        <main className="canvas-container">
          {currentProject ? (
            <Canvas
              project={currentProject}
              canvasMeta={canvasMeta}
              sections={sections}
              selectedSection={selectedSection}
              onSelectSection={handleSelectSection}
              onNodeMove={handleNodeMove}
            />
          ) : (
            <div className="empty-state">
              <p>Select or create a project to get started</p>
            </div>
          )}
        </main>

        {selectedSection && (
          <NodeEditor
            sectionName={selectedSection}
            content={sectionContent}
            onContentChange={setSectionContent}
            onSave={handleSaveSection}
            onValidate={handleValidate}
            validationResults={validationResults}
            loading={loading}
          />
        )}
      </div>

      {showGenerateModal && (
        <GenerateModal
          onGenerate={handleGenerate}
          onClose={() => setShowGenerateModal(false)}
        />
      )}

      {toast && (
        <div className={`toast toast-${toast.type}`}>{toast.msg}</div>
      )}
    </div>
  )
}
