import React, { useState } from 'react';
import './ColorPicker.css';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  label?: string;
}

const PRESET_COLORS = [
  '#e94560', // highlight red
  '#1a1a2e', // primary dark
  '#0f3460', // accent blue
  '#2ecc71', // success green
  '#3498db', // info blue
  '#f39c12', // warning orange
  '#9b59b6', // purple
  '#e74c3c', // danger red
  '#1abc9c', // turquoise
  '#34495e', // dark gray
  '#95a5a6', // light gray
  '#ecf0f1', // white gray
  '#ff6b6b', // coral
  '#4ecdc4', // cyan
  '#45b7d1', // sky blue
  '#f7b731', // yellow
  '#5f27cd', // deep purple
  '#00d2d3', // aqua
];

const ColorPicker: React.FC<ColorPickerProps> = ({ value, onChange, label }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customColor, setCustomColor] = useState(value);

  const handlePresetClick = (color: string) => {
    onChange(color);
    setCustomColor(color);
    setIsOpen(false);
  };

  const handleCustomColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newColor = e.target.value;
    setCustomColor(newColor);
    onChange(newColor);
  };

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleClickOutside = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      setIsOpen(false);
    }
  };

  return (
    <div className="color-picker-container">
      {label && <label className="color-picker-label">{label}</label>}
      
      <div className="color-picker-trigger" onClick={handleToggle}>
        <div 
          className="color-preview" 
          style={{ backgroundColor: value }}
          title={value}
        />
        <span className="color-value">{value}</span>
        <svg 
          className={`dropdown-icon ${isOpen ? 'open' : ''}`}
          width="12" 
          height="12" 
          viewBox="0 0 12 12"
        >
          <path 
            d="M2 4l4 4 4-4" 
            stroke="currentColor" 
            strokeWidth="2" 
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {isOpen && (
        <div className="color-picker-overlay" onClick={handleClickOutside}>
          <div className="color-picker-dropdown">
            <div className="color-picker-section">
              <div className="section-title">预设颜色</div>
              <div className="preset-colors-grid">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color}
                    className={`preset-color-item ${value === color ? 'active' : ''}`}
                    style={{ backgroundColor: color }}
                    onClick={() => handlePresetClick(color)}
                    title={color}
                    type="button"
                  >
                    {value === color && (
                      <svg width="16" height="16" viewBox="0 0 16 16">
                        <path
                          d="M13 4L6 11 3 8"
                          stroke="white"
                          strokeWidth="2"
                          fill="none"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="color-picker-section">
              <div className="section-title">自定义颜色</div>
              <div className="custom-color-input-wrapper">
                <input
                  type="color"
                  className="custom-color-input"
                  value={customColor}
                  onChange={handleCustomColorChange}
                />
                <input
                  type="text"
                  className="custom-color-text"
                  value={customColor}
                  onChange={(e) => {
                    const newValue = e.target.value;
                    setCustomColor(newValue);
                    if (/^#[0-9A-Fa-f]{6}$/.test(newValue)) {
                      onChange(newValue);
                    }
                  }}
                  placeholder="#000000"
                  maxLength={7}
                />
              </div>
            </div>

            <div className="color-picker-actions">
              <button 
                className="btn-picker-cancel" 
                onClick={() => setIsOpen(false)}
                type="button"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ColorPicker;