import React, { useState, useRef, useEffect } from 'react';
import './ColorPicker.css';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  className?: string;
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
  '#ffe66d', // yellow
  '#a8e6cf', // mint
  '#ff8b94', // pink
  '#c7ceea', // lavender
];

const ColorPicker: React.FC<ColorPickerProps> = ({ value, onChange, className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customColor, setCustomColor] = useState(value);
  const pickerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setCustomColor(value);
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleColorSelect = (color: string) => {
    onChange(color);
    setCustomColor(color);
  };

  const handleCustomColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newColor = e.target.value;
    setCustomColor(newColor);
    onChange(newColor);
  };

  const handleHexInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let hex = e.target.value;
    if (!hex.startsWith('#')) {
      hex = '#' + hex;
    }
    if (/^#[0-9A-Fa-f]{0,6}$/.test(hex)) {
      setCustomColor(hex);
      if (hex.length === 7) {
        onChange(hex);
      }
    }
  };

  const togglePicker = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={`color-picker ${className}`} ref={pickerRef}>
      <div className="color-picker-trigger" onClick={togglePicker}>
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
        <div className="color-picker-dropdown">
          <div className="color-picker-section">
            <label className="color-picker-label">预设颜色</label>
            <div className="preset-colors">
              {PRESET_COLORS.map((color) => (
                <button
                  key={color}
                  className={`preset-color ${value === color ? 'active' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => handleColorSelect(color)}
                  title={color}
                  type="button"
                >
                  {value === color && (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path
                        d="M13 4L6 11L3 8"
                        stroke="white"
                        strokeWidth="2"
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
            <label className="color-picker-label">自定义颜色</label>
            <div className="custom-color-input">
              <input
                ref={inputRef}
                type="color"
                value={customColor}
                onChange={handleCustomColorChange}
                className="color-input"
              />
              <input
                type="text"
                value={customColor}
                onChange={handleHexInputChange}
                placeholder="#000000"
                className="hex-input"
                maxLength={7}
              />
            </div>
          </div>

          <div className="color-picker-actions">
            <button
              className="btn-reset"
              onClick={() => handleColorSelect('#e94560')}
              type="button"
            >
              重置为默认
            </button>
            <button
              className="btn-close"
              onClick={() => setIsOpen(false)}
              type="button"
            >
              完成
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ColorPicker;