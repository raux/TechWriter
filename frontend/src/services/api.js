import axios from 'axios'

const BASE_URL = '/api'

const api = axios.create({ baseURL: BASE_URL })

// Projects
export const listProjects = () => api.get('/projects/')
export const createProject = (projectName) => api.post('/projects/', { project_name: projectName })

// Sections
export const listSections = (project) => api.get(`/projects/${project}/sections/`)
export const getSection = (project, sectionName) => api.get(`/projects/${project}/sections/${sectionName}`)
export const createSection = (project, sectionName, content) =>
  api.post(`/projects/${project}/sections/${sectionName}`, { content })
export const updateSection = (project, sectionName, content) =>
  api.put(`/projects/${project}/sections/${sectionName}`, { content })
export const deleteSection = (project, sectionName) =>
  api.delete(`/projects/${project}/sections/${sectionName}`)

// Canvas
export const getCanvasMeta = (project) => api.get(`/projects/${project}/canvas/`)
export const updateCanvasMeta = (project, meta) => api.put(`/projects/${project}/canvas/`, meta)
export const moveNode = (project, nodeId, x, y) =>
  api.patch(`/projects/${project}/canvas/nodes/${nodeId}/position`, { x, y })

// Generate
export const generateSection = (project, sectionType, sectionName, additionalContext = '') =>
  api.post(`/projects/${project}/generate/`, {
    section_type: sectionType,
    section_name: sectionName,
    additional_context: additionalContext,
  })

// Validate
export const validateSection = (project, sectionName) =>
  api.post(`/projects/${project}/validate/section`, { section_name: sectionName })
export const checkConsistency = (project) =>
  api.post(`/projects/${project}/validate/consistency`)
