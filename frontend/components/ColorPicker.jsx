import React, { useState } from 'react';

const ColorPicker = ({ value = '#e94560', onChange, label = '选择颜色' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customColor, setCustomColor] = useState(value);

  const presetColors = [
    '#e94560', // highlight (default)
    '#3498db', // blue
    '#2ecc71', // green
    '#f39c12', // orange
    '#9b59b6', // purple
    '#e74c3c', // red
    '#1abc9c', // turquoise
    '#34495e', // dark gray
    '#f1c40f', // yellow
    '#e67e22', // carrot
    '#95a5a6', // gray
    '#2c3e50', // midnight blue
    '#c0392b', // dark red
    '#8e44ad', // wisteria
    '#16a085', // green sea
    '#27ae60', // nephritis
    '#d35400', // pumpkin
    '#c0392b', // pomegranate
  ];

  const handleColorSelect = (color) => {
    setCustomColor(color);
    if (onChange) {
      onChange(color);
    }
    setIsOpen(false);
  };

  const handleCustomColorChange = (e) => {
    const color = e.target.value;
    setCustomColor(color);
    if (onChange) {
      onChange(color);
    }
  };

  return (
    <div className="color-picker-wrapper">
      <style>{`
        .color-picker-wrapper {
          position: relative;
          width: 100%;
        }

        .color-picker-label {
          display: block;
          font-size: 0.9em;
          opacity: 0.8;
          margin-bottom: 8px;
          color: var(--text, #f1f1f1);
        }

        .color-picker-trigger {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .color-picker-trigger:hover {
          background: rgba(255, 255, 255, 0.12);
          border-color: rgba(255, 255, 255, 0.2);
          transform: translateY(-1px);
        }

        .color-preview {
          width: 32px;
          height: 32px;
          border-radius: 4px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
          transition: transform 0.2s ease;
        }

        .color-picker-trigger:hover .color-preview {
          transform: scale(1.1);
        }

        .color-value-text {
          flex: 1;
          font-family: 'Courier New', monospace;
          font-size: 0.95em;
          color: var(--text, #f1f1f1);
          font-weight: 600;
        }

        .color-picker-dropdown {
          position: absolute;
          top: calc(100% + 8px);
          left: 0;
          right: 0;
          background: rgba(26, 26, 46, 0.98);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 8px;
          padding: 16px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
          backdrop-filter: blur(10px);
          z-index: 1000;
          opacity: 0;
          transform: translateY(-10px);
          pointer-events: none;
          transition: all 0.3s ease;
        }

        .color-picker-dropdown.open {
          opacity: 1;
          transform: translateY(0);
          pointer-events: all;
        }

        .color-picker-section {
          margin-bottom: 16px;
        }

        .color-picker-section:last-child {
          margin-bottom: 0;
        }

        .color-picker-section-title {
          font-size: 0.85em;
          opacity: 0.7;
          margin-bottom: 10px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--text, #f1f1f1);
        }

        .preset-colors-grid {
          display: grid;
          grid-template-columns: repeat(6, 1fr);
          gap: 8px;
        }

        .preset-color-item {
          width: 100%;
          aspect-ratio: 1;
          border-radius: 4px;
          border: 2px solid transparent;
          cursor: pointer;
          transition: all 0.2s ease;
          position: relative;
        }

        .preset-color-item:hover {
          transform: scale(1.15);
          border-color: rgba(255, 255, 255, 0.5);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .preset-color-item.selected {
          border-color: rgba(255, 255, 255, 0.8);
          box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.5);
        }

        .preset-color-item.selected::after {
          content: '✓';
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          color: white;
          font-weight: bold;
          font-size: 14px;
          text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }

        .custom-color-input-wrapper {
          display: flex;
          gap: 10px;
          align-items: center;
        }

        .custom-color-input {
          flex: 1;
          padding: 10px 12px;
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text, #f1f1f1);
          font-family: 'Courier New', monospace;
          font-size: 0.95em;
          transition: all 0.3s ease;
        }

        .custom-color-input:focus {
          outline: none;
          background: rgba(255, 255, 255, 0.12);
          border-color: var(--highlight, #e94560);
        }

        .native-color-picker {
          width: 50px;
          height: 40px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          background: transparent;
        }

        .native-color-picker::-webkit-color-swatch-wrapper {
          padding: 0;
        }

        .native-color-picker::-webkit-color-swatch {
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 4px;
        }

        .color-picker-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 999;
          display: none;
        }

        .color-picker-overlay.open {
          display: block;
        }

        @media (max-width: 768px) {
          .preset-colors-grid {
            grid-template-columns: repeat(4, 1fr);
          }

          .color-picker-dropdown {
            left: 50%;
            right: auto;
            transform: translateX(-50%) translateY(-10px);
            width: 90vw;
            max-width: 320px;
          }

          .color-picker-dropdown.open {
            transform: translateX(-50%) translateY(0);
          }
        }
      `}</style>

      {label && <div className="color-picker-label">{label}</div>}

      <div
        className="color-picker-trigger"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div
          className="color-preview"
          style={{ backgroundColor: customColor }}
        />
        <span className="color-value-text">{customColor.toUpperCase()}</span>
      </div>

      <div
        className={`color-picker-overlay ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(false)}
      />

      <div className={`color-picker-dropdown ${isOpen ? 'open' : ''}`}>
        <div className="color-picker-section">
          <div className="color-picker-section-title">预设颜色</div>
          <div className="preset-colors-grid">
            {presetColors.map((color) => (
              <div
                key={color}
                className={`preset-color-item ${
                  customColor.toLowerCase() === color.toLowerCase()
                    ? 'selected'
                    : ''
                }`}
                style={{ backgroundColor: color }}
                onClick={() => handleColorSelect(color)}
                title={color}
              />
            ))}
          </div>
        </div>

        <div className="color-picker-section">
          <div className="color-picker-section-title">自定义颜色</div>
          <div className="custom-color-input-wrapper">
            <input
              type="text"
              className="custom-color-input"
              value={customColor}
              onChange={handleCustomColorChange}
              placeholder="#000000"
              pattern="^#[0-9A-Fa-f]{6}$"
            />
            <input
              type="color"
              className="native-color-picker"
              value={customColor}
              onChange={handleCustomColorChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ColorPicker;