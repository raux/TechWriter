import React, { useCallback, useEffect } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import SectionNode from './SectionNode.jsx'
import { moveNode } from '../services/api.js'

const NODE_TYPES = { sectionNode: SectionNode }

const SECTION_POSITIONS = {
  introduction: { x: 50, y: 50 },
  data_preparation: { x: 300, y: 50 },
  rqs: { x: 550, y: 50 },
  glossary: { x: 800, y: 50 },
  methodology: { x: 100, y: 250 },
  results: { x: 400, y: 250 },
  discussion: { x: 100, y: 450 },
  related_work: { x: 400, y: 450 },
  conclusion: { x: 700, y: 450 },
}

const GRID_COLUMNS = 4
const GRID_CELL_WIDTH = 250
const GRID_CELL_HEIGHT = 200
const GRID_OFFSET = 50

function getDefaultPosition(sectionName, index) {
  for (const [key, pos] of Object.entries(SECTION_POSITIONS)) {
    if (sectionName.toLowerCase().includes(key.replace('_', ''))) {
      return pos
    }
  }
  return {
    x: (index % GRID_COLUMNS) * GRID_CELL_WIDTH + GRID_OFFSET,
    y: Math.floor(index / GRID_COLUMNS) * GRID_CELL_HEIGHT + GRID_OFFSET,
  }
}

function getSectionType(sectionName) {
  const types = ['introduction', 'data_preparation', 'rqs', 'methodology', 'results', 'discussion', 'related_work', 'conclusion', 'glossary']
  for (const t of types) {
    if (sectionName.toLowerCase().includes(t.replace('_', ''))) return t
  }
  return 'custom'
}

function buildNodes(sections, canvasMeta, selectedSection, onSelectSection) {
  const nodeMap = {}
  for (const node of (canvasMeta.nodes || [])) {
    nodeMap[node.id || node.section_name] = node
  }

  return sections.map((sectionName, i) => {
    const saved = nodeMap[sectionName]
    const position = saved
      ? { x: saved.x, y: saved.y }
      : getDefaultPosition(sectionName, i)
    return {
      id: sectionName,
      type: 'sectionNode',
      position,
      data: {
        sectionName,
        sectionType: saved?.section_type || getSectionType(sectionName),
        selected: selectedSection === sectionName,
        onSelect: onSelectSection,
      },
    }
  })
}

export default function Canvas({ project, canvasMeta, sections, selectedSection, onSelectSection, onNodeMove }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    const built = buildNodes(sections, canvasMeta, selectedSection, onSelectSection)
    setNodes(built)
  }, [sections, canvasMeta, selectedSection])

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    []
  )

  const onNodeDragStop = useCallback(
    async (event, node) => {
      const { x, y } = node.position
      onNodeMove(node.id, x, y)
      try {
        await moveNode(project, node.id, x, y)
      } catch (e) {
        console.warn('Failed to persist node position', e)
      }
    },
    [project, onNodeMove]
  )

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onNodeDragStop={onNodeDragStop}
      nodeTypes={NODE_TYPES}
      fitView
      fitViewOptions={{ padding: 0.2 }}
      style={{ background: '#0f1117' }}
    >
      <Background color="#1e2235" gap={20} size={1} />
      <Controls style={{ background: '#1a1d27', border: '1px solid #2d3048' }} />
      <MiniMap
        style={{ background: '#131620', border: '1px solid #2d3048' }}
        nodeColor="#7c8cf8"
        maskColor="rgba(0,0,0,0.6)"
      />
      <Panel position="top-right" style={{ color: '#4a5568', fontSize: '0.75rem' }}>
        {sections.length} sections • drag to reposition
      </Panel>
    </ReactFlow>
  )
}
