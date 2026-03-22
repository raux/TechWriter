import React from 'react'
import { Handle, Position } from '@xyflow/react'
import './SectionNode.css'

const TYPE_COLORS = {
  introduction: '#3b82f6',
  data_preparation: '#8b5cf6',
  rqs: '#f59e0b',
  methodology: '#10b981',
  results: '#06b6d4',
  discussion: '#f97316',
  related_work: '#6366f1',
  conclusion: '#ec4899',
  glossary: '#84cc16',
  custom: '#94a3b8',
}

const TYPE_ICONS = {
  introduction: '📝',
  data_preparation: '💾',
  rqs: '❓',
  methodology: '🔬',
  results: '📊',
  discussion: '💬',
  related_work: '🔗',
  conclusion: '🎯',
  glossary: '📚',
  custom: '📄',
}

export default function SectionNode({ data }) {
  const { sectionName, sectionType, selected, onSelect } = data
  const color = TYPE_COLORS[sectionType] || TYPE_COLORS.custom
  const icon = TYPE_ICONS[sectionType] || TYPE_ICONS.custom

  return (
    <div
      className={`section-node ${selected ? 'selected' : ''}`}
      style={{ '--node-color': color }}
      onClick={() => onSelect(sectionName)}
    >
      <Handle type="target" position={Position.Top} />
      <div className="node-header">
        <span className="node-icon">{icon}</span>
        <span className="node-type">{sectionType?.replace(/_/g, ' ')}</span>
      </div>
      <div className="node-name">{sectionName.replace(/_/g, ' ')}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}
