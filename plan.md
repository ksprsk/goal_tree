# Goal Tree Application Specification

## Overview

Browser-based Python GUI application for goal/task management using RRTD (Resource-Rational Task Decomposition) and DAPP (Dynamic Adaptive Policy Pathways) frameworks.

---

## Data Model

### Node Types

Two node types exist: `Base` and `DAPP_Child`

#### Base Node

Used for: Root nodes, RRTD children (subgoals)
```
Base Node:
├── id: unique identifier
├── name: string (required)
├── description: string (optional)
├── status: enum [진행중, 완료, 보류, 취소, 실패]
├── completion_condition: string (optional, "what counts as done")
├── children_type: enum [LEAF, RRTD, DAPP] (default: LEAF)
├── children: list of nodes (type determined by children_type)
├── progress_board: string (free text)
└── content_board: string (free text)
```

#### DAPP_Child Node

Used for: Children of DAPP-type nodes (scenario/strategy nodes)
```
DAPP_Child Node:
├── id: unique identifier
├── name: string (required)
├── description: string (optional)
├── status: enum [진행중, 완료, 보류, 취소, 실패]
├── completion_condition: string (optional)
├── children_type: enum [LEAF, RRTD, DAPP] (default: LEAF)
├── children: list of nodes (type determined by children_type)
├── progress_board: string (free text)
├── content_board: string (free text)
│
│ # DAPP-specific fields (required for this type)
├── atp: list of strings (minimum 1 required)
├── signposts: list of strings (can be empty)
└── triggers: list of strings (can be empty)
```

### Children Type Rules
```
children_type determines child node type:

LEAF → no children allowed
RRTD → children are Base nodes (subgoals/bottlenecks)
DAPP → children are DAPP_Child nodes (scenarios/strategies)
```

### Children Type Lifecycle
```
1. Node created → children_type = LEAF (fixed)
2. First child added → user selects RRTD or DAPP (one-time choice)
3. After first child → children_type immutable
4. Children are never deleted (use status: 취소 instead)
```

---

## Data Structure (Forest)
```
Application Data:
├── roots: list of Base nodes (multiple independent goal trees)
└── metadata: { last_modified, version, etc. }
```

Example structure:
```
roots:
├── Base Node (Goal A)
│   ├── children_type: RRTD
│   └── children:
│       ├── Base Node (Subgoal A1)
│       │   ├── children_type: DAPP
│       │   └── children:
│       │       ├── DAPP_Child (Strategy 1)
│       │       │   ├── atp: ["condition X within 2 weeks"]
│       │       │   ├── signposts: ["metric Y"]
│       │       │   ├── triggers: ["if Y < 50%"]
│       │       │   ├── children_type: RRTD
│       │       │   └── children:
│       │       │       └── Base Node (Sub-subgoal)
│       │       └── DAPP_Child (Strategy 2)
│       │           ├── atp: ["condition Z"]
│       │           └── children_type: LEAF
│       └── Base Node (Subgoal A2)
│           └── children_type: LEAF
│
└── Base Node (Goal B)
    └── children_type: LEAF
```

---

## GUI Layout
```
┌─────────────────────────────────────────────────────────────────────┐
│                         Application                                  │
├──────────────────────┬──────────────────────────────────────────────┤
│                      │                                              │
│                      │  ┌─────────────────────────────────────────┐ │
│                      │  │         Node Fields Panel               │ │
│                      │  │  (name, status, completion_condition,   │ │
│                      │  │   ATP/signposts/triggers if DAPP_Child) │ │
│                      │  │         [editable]                      │ │
│      Tree View       │  ├─────────────────────────────────────────┤ │
│                      │  │                                         │ │
│   [collapsible]      │  │  Progress Board    │   Content Board    │ │
│   [color by status]  │  │                    │                    │ │
│   [icon by type]     │  │  (free text)       │   (free text)      │ │
│                      │  │  (user-written)    │   (external info)  │ │
│                      │  │                    │                    │ │
│                      │  │                    │                    │ │
│                      │  │                    │                    │ │
│                      │  └─────────────────────────────────────────┘ │
│                      │                                              │
└──────────────────────┴──────────────────────────────────────────────┘
```

### Tree View Features
```
Visual Indicators:
├── Node type distinction:
│   ├── Base node: icon/symbol A (e.g., ●)
│   └── DAPP_Child node: icon/symbol B (e.g., ◆)
│
├── Children type distinction:
│   ├── RRTD: indicator (e.g., [R] or specific color border)
│   ├── DAPP: indicator (e.g., [D] or specific color border)  
│   └── LEAF: no indicator (or [L])
│
├── Status colors:
│   ├── 진행중: blue
│   ├── 완료: green
│   ├── 보류: gray
│   ├── 취소: light gray / strikethrough
│   └── 실패: red
│
└── Collapse/Expand: clickable toggle per node
```

### Right Panel Layout
```
┌─────────────────────────────────────────┐
│ Node Fields Panel (top section)         │
│ ─────────────────────────────────────── │
│ Name: [editable text field]             │
│ Description: [editable text area]       │
│ Status: [dropdown]                      │
│ Completion Condition: [editable]        │
│                                         │
│ [If DAPP_Child:]                        │
│ ATP: [list, add/edit/delete]            │
│ Signposts: [list, add/edit/delete]      │
│ Triggers: [list, add/edit/delete]       │
├─────────────────────────────────────────┤
│ Progress Board    │   Content Board     │
│ (50% width)       │   (50% width)       │
│                   │                     │
│ [free text area]  │   [free text area]  │
│                   │                     │
└─────────────────────────────────────────┘
```

---

## User Interactions

### Tree Operations
```
Create root node:
└── Button/action to add new root (Base node)

Add child to node:
├── If children_type == LEAF:
│   └── Prompt: "Choose type: RRTD (subgoals) or DAPP (scenarios)"
│       ├── RRTD selected → children_type = RRTD, create Base child
│       └── DAPP selected → children_type = DAPP, create DAPP_Child
│
├── If children_type == RRTD:
│   └── Create Base node as child
│
└── If children_type == DAPP:
    └── Create DAPP_Child node as child (with empty ATP prompt)

Select node:
└── Click node → load node data in right panel

Collapse/Expand:
└── Toggle visibility of children
```

### Node Field Editing
```
All fields editable in Node Fields Panel
Changes auto-save or explicit save button

For DAPP_Child ATP field:
├── Must have at least 1 entry
├── Add button to create new ATP entry
├── Edit inline
└── Delete allowed only if more than 1 remains

For Signposts/Triggers:
├── Can be empty
├── Add/Edit/Delete freely
```

### Board Editing
```
Progress Board: free text area, saves per node
Content Board: free text area, saves per node
```

---

## Persistence

### Storage Format: JSON
```json
{
  "version": "1.0",
  "last_modified": "2024-12-03T15:30:00Z",
  "roots": [
    {
      "id": "uuid-1",
      "type": "Base",
      "name": "Goal A",
      "description": "...",
      "status": "진행중",
      "completion_condition": "...",
      "children_type": "RRTD",
      "progress_board": "...",
      "content_board": "...",
      "children": [
        {
          "id": "uuid-2",
          "type": "Base",
          "name": "Subgoal A1",
          ...
        }
      ]
    }
  ]
}
```

For DAPP_Child nodes, additional fields:
```json
{
  "id": "uuid-3",
  "type": "DAPP_Child",
  "name": "Strategy 1",
  "description": "...",
  "status": "진행중",
  "completion_condition": "...",
  "children_type": "LEAF",
  "progress_board": "...",
  "content_board": "...",
  "atp": ["condition X within 2 weeks"],
  "signposts": ["metric Y", "metric Z"],
  "triggers": ["if Y < 50%"],
  "children": []
}
```

### File Location
```
Default: application directory / data.json
Auto-save on changes (debounced)
Load on application start
```

---

## Technical Requirements
```
Language: Python
GUI Framework: Browser-based (suggest: Flask + HTML/CSS/JS, or Streamlit, or NiceGUI)
Persistence: JSON file
```

---

## NOT in Scope (MVP)
```
- Node move/reorder
- Search
- Undo/history
- Node deletion (use 취소 status instead)
- Attachments
- Multiple save files
```

---

## Summary

Core concept:
1. Forest of goal trees (multiple roots)
2. Each node is either Base or DAPP_Child
3. Each node's children_type determines if children are subgoals (RRTD→Base) or scenarios (DAPP→DAPP_Child) or none (LEAF)
4. DAPP_Child has extra fields: ATP (1+), Signposts, Triggers
5. All nodes have Progress Board and Content Board (free text)
6. Visual distinction by node type, children type, and status