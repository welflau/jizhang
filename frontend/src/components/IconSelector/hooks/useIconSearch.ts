import { useState, useCallback, useMemo } from 'react';

interface UseIconSearchProps {
  icons: string[];
  categories?: Record<string, string[]>;
}

interface UseIconSearchReturn {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  filteredIcons: string[];
  selectedCategory: string;
  setSelectedCategory: (category: string) => void;
  clearSearch: () => void;
  hasResults: boolean;
  totalResults: number;
}

/**
 * 图标搜索 Hook
 * 提供图标搜索、过滤和分类功能
 */
export const useIconSearch = ({
  icons,
  categories = {}
}: UseIconSearchProps): UseIconSearchReturn => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  /**
   * 根据搜索词和分类过滤图标
   */
  const filteredIcons = useMemo(() => {
    let result = icons;

    // 按分类过滤
    if (selectedCategory !== 'all' && categories[selectedCategory]) {
      result = categories[selectedCategory];
    }

    // 按搜索词过滤
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      result = result.filter(icon => {
        const iconName = icon.toLowerCase();
        
        // 支持多种搜索方式
        return (
          iconName.includes(term) ||
          iconName.replace(/-/g, '').includes(term.replace(/\s/g, '')) ||
          iconName.split('-').some(part => part.startsWith(term))
        );
      });
    }

    return result;
  }, [icons, searchTerm, selectedCategory, categories]);

  /**
   * 清空搜索
   */
  const clearSearch = useCallback(() => {
    setSearchTerm('');
    setSelectedCategory('all');
  }, []);

  /**
   * 是否有搜索结果
   */
  const hasResults = filteredIcons.length > 0;

  /**
   * 搜索结果总数
   */
  const totalResults = filteredIcons.length;

  return {
    searchTerm,
    setSearchTerm,
    filteredIcons,
    selectedCategory,
    setSelectedCategory,
    clearSearch,
    hasResults,
    totalResults
  };
};

export default useIconSearch;