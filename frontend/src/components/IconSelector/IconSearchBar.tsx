import React, { useState, useCallback } from 'react';
import './IconSearchBar.css';

interface IconSearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  className?: string;
}

const IconSearchBar: React.FC<IconSearchBarProps> = ({
  onSearch,
  placeholder = '搜索图标...',
  className = ''
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch(query);
  }, [onSearch]);

  const handleClear = useCallback(() => {
    setSearchQuery('');
    onSearch('');
  }, [onSearch]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  return (
    <div className={`icon-search-bar ${isFocused ? 'focused' : ''} ${className}`}>
      <div className="search-input-wrapper">
        <svg 
          className="search-icon" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        
        <input
          type="text"
          className="search-input"
          placeholder={placeholder}
          value={searchQuery}
          onChange={handleSearchChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          autoComplete="off"
          spellCheck="false"
        />
        
        {searchQuery && (
          <button
            className="clear-button"
            onClick={handleClear}
            type="button"
            aria-label="清除搜索"
          >
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        )}
      </div>
      
      {searchQuery && (
        <div className="search-info">
          搜索: <span className="search-query">{searchQuery}</span>
        </div>
      )}
    </div>
  );
};

export default IconSearchBar;