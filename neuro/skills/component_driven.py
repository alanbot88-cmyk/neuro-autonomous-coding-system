"""
Component Driven Development Skill
Storybook, atomic design, component API design, testing
"""

from typing import Dict, List, Any, Optional


class ComponentDrivenSkill:
    """
    Component-driven development skill for building UI from components.
    Handles Storybook, atomic design, props API, composition patterns.
    """
    
    NAME = "component_driven"
    DESCRIPTION = "Component-driven development - Storybook, atomic design, props API, component composition, testing"
    TRIGGERS = [
        "component", "storybook", "atomic", "design system",
        "props", "composition", "ui library", "component api",
        "atomic design", "atoms", "molecules", "organisms"
    ]
    
    @classmethod
    def get_atomic_design_templates(cls) -> str:
        """Get atomic design component templates"""
        return '''
// Atomic Design Component Structure

// ATOMS - Basic building blocks
// atoms/Button.tsx
export interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onClick?: () => void
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

// atoms/Input.tsx
export interface InputProps {
  label: string
  placeholder?: string
  value: string
  onChange: (value: string) => void
  error?: string
  disabled?: boolean
}

export const Input: React.FC<InputProps> = ({
  label,
  placeholder,
  value,
  onChange,
  error,
  disabled
}) => {
  return (
    <div className="input-wrapper">
      <label>{label}</label>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={error ? 'error' : ''}
      />
      {error && <span className="error-text">{error}</span>}
    </div>
  )
}

// MOLECULES - Combinations of atoms
// molecules/SearchBar.tsx
import { Input } from '../atoms/Input'
import { Button } from '../atoms/Button'

export interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  placeholder?: string
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSubmit,
  placeholder = 'Search...'
}) => {
  return (
    <div className="search-bar">
      <Input
        label=""
        value={value}
        onChange={onChange}
        placeholder={placeholder}
      />
      <Button onClick={onSubmit}>Search</Button>
    </div>
  )
}

// ORGANISMS - Complex UI sections
// organisms/Header.tsx
import { Button } from '../atoms/Button'
import { SearchBar } from '../molecules/SearchBar'
import { Navigation } from '../molecules/Navigation'

export interface HeaderProps {
  logo: string
  onSearch: (query: string) => void
  onLogin: () => void
}

export const Header: React.FC<HeaderProps> = ({
  logo,
  onSearch,
  onLogin
}) => {
  const [searchValue, setSearchValue] = useState('')
  
  return (
    <header className="header">
      <div className="header-left">
        <img src={logo} alt="Logo" className="logo" />
        <Navigation />
      </div>
      <div className="header-center">
        <SearchBar
          value={searchValue}
          onChange={setSearchValue}
          onSubmit={() => onSearch(searchValue)}
        />
      </div>
      <div className="header-right">
        <Button variant="ghost" onClick={onLogin}>Login</Button>
      </div>
    </header>
  )
}

// TEMPLATES - Page layouts without data
// templates/PageTemplate.tsx
export interface PageTemplateProps {
  header: React.ReactNode
  sidebar: React.ReactNode
  content: React.ReactNode
  footer: React.ReactNode
}

export const PageTemplate: React.FC<PageTemplateProps> = ({
  header, sidebar, content, footer
}) => {
  return (
    <div className="page">
      <header>{header}</header>
      <div className="page-body">
        <aside>{sidebar}</aside>
        <main>{content}</main>
      </div>
      <footer>{footer}</footer>
    </div>
  )
}
'''

    @classmethod
    def get_storybook_templates(cls) -> str:
        """Get Storybook component templates"""
        return '''
// Storybook Component Stories
// ComponentName.stories.tsx

import type { Meta, StoryObj } from '@storybook/react'
import { ComponentName } from './ComponentName'

const meta: Meta<typeof ComponentName> = {
  title: 'Components/ComponentName',
  component: ComponentName,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Description of the component'
      }
    }
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'ghost'],
      description: 'Visual variant'
    },
    size: {
      control: { type: 'radio' },
      options: ['sm', 'md', 'lg']
    }
  }
}

export default meta
type Story = StoryObj<typeof meta>

// Basic story
export const Basic: Story = {
  args: {
    children: 'Click me',
    variant: 'primary'
  }
}

// All variants
export const Variants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <ComponentName variant="primary">Primary</ComponentName>
      <ComponentName variant="secondary">Secondary</ComponentName>
      <ComponentName variant="ghost">Ghost</ComponentName>
    </div>
  )
}

// Interactive playground
export const Playground: Story = {
  args: {
    children: 'Play with me!',
    variant: 'primary',
    size: 'md'
  },
  argTypes: {
    onClick: { action: 'clicked' }
  }
}

// States
export const States: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <ComponentName>Default</ComponentName>
      <ComponentName disabled>Disabled</ComponentName>
      <ComponentName onClick={() => alert('Clicked!')}>With Click</ComponentName>
    </div>
  )
}
'''

    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()
        
        result_type = "atomic"
        if "storybook" in task_lower or "story" in task_lower:
            result_type = "storybook"
        elif "atomic" in task_lower:
            result_type = "atomic"
        elif "composition" in task_lower or "compose" in task_lower:
            result_type = "composition"
        
        templates = {
            "atomic": cls.get_atomic_design_templates(),
            "storybook": cls.get_storybook_templates(),
        }
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "template": templates.get(result_type, templates["atomic"]),
            "atomic_levels": {
                "atoms": "Basic HTML elements, buttons, inputs, labels",
                "molecules": "Simple component groups, search bar, form fields",
                "organisms": "Complex UI sections, header, cards, forms",
                "templates": "Page layouts without data",
                "pages": "Templates with real data"
            },
            "tips": [
                "Start with atoms, compose to molecules",
                "Use compound components for flexible APIs",
                "Storybook autodocs for documentation",
                "Test each component in isolation"
            ]
        }


def generate_component(task: str, **kwargs) -> Dict[str, Any]:
    return ComponentDrivenSkill.invoke(task, kwargs)
