import { useState, useCallback, useMemo } from 'react';

export interface IconItem {
  name: string;
  component: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  category?: string;
  tags?: string[];
}

export interface UseIconSelectionProps {
  icons: IconItem[];
  initialSelected?: string;
  onSelect?: (iconName: string) => void;
}

export interface UseIconSelectionReturn {
  selectedIcon: string | null;
  searchQuery: string;
  selectedCategory: string;
  filteredIcons: IconItem[];
  categories: string[];
  handleIconSelect: (iconName: string) => void;
  handleSearchChange: (query: string) => void;
  handleCategoryChange: (category: string) => void;
  clearSelection: () => void;
  getIconByName: (name: string) => IconItem | undefined;
}

export const useIconSelection = ({
  icons,
  initialSelected,
  onSelect,
}: UseIconSelectionProps): UseIconSelectionReturn => {
  const [selectedIcon, setSelectedIcon] = useState<string | null>(
    initialSelected || null
  );
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Extract unique categories from icons
  const categories = useMemo(() => {
    const categorySet = new Set<string>();
    categorySet.add('all');
    
    icons.forEach((icon) => {
      if (icon.category) {
        categorySet.add(icon.category);
      }
    });
    
    return Array.from(categorySet);
  }, [icons]);

  // Filter icons based on search query and category
  const filteredIcons = useMemo(() => {
    let result = icons;

    // Filter by category
    if (selectedCategory !== 'all') {
      result = result.filter((icon) => icon.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      result = result.filter((icon) => {
        const nameMatch = icon.name.toLowerCase().includes(query);
        const tagsMatch = icon.tags?.some((tag) =>
          tag.toLowerCase().includes(query)
        );
        return nameMatch || tagsMatch;
      });
    }

    return result;
  }, [icons, searchQuery, selectedCategory]);

  // Handle icon selection
  const handleIconSelect = useCallback(
    (iconName: string) => {
      setSelectedIcon(iconName);
      onSelect?.(iconName);
    },
    [onSelect]
  );

  // Handle search query change
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Handle category change
  const handleCategoryChange = useCallback((category: string) => {
    setSelectedCategory(category);
  }, []);

  // Clear selection
  const clearSelection = useCallback(() => {
    setSelectedIcon(null);
  }, []);

  // Get icon by name
  const getIconByName = useCallback(
    (name: string): IconItem | undefined => {
      return icons.find((icon) => icon.name === name);
    },
    [icons]
  );

  return {
    selectedIcon,
    searchQuery,
    selectedCategory,
    filteredIcons,
    categories,
    handleIconSelect,
    handleSearchChange,
    handleCategoryChange,
    clearSelection,
    getIconByName,
  };
};

export default useIconSelection;