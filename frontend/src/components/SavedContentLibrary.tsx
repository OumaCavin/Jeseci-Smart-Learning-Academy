import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';

interface SavedContent {
  id: string;
  title: string;
  type: 'snippet' | 'lesson' | 'discussion' | 'resource';
  description: string;
  savedAt: string;
  tags: string[];
  author?: string;
  thumbnail?: string;
}

const SavedContentLibrary: React.FC = () => {
  const [savedContent, setSavedContent] = useState<SavedContent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedContent, setSelectedContent] = useState<SavedContent | null>(null);

  useEffect(() => {
    loadSavedContent();
  }, []);

  const loadSavedContent = async () => {
    try {
      setIsLoading(true);
      const response = await ApiService.getSavedContent();
      setSavedContent(response);
    } catch (error) {
      console.error('Error loading saved content:', error);
      // Use mock data for demo
      setSavedContent([
        {
          id: '1',
          title: 'Introduction to Neural Networks',
          type: 'lesson',
          description: 'A comprehensive guide to understanding neural network fundamentals',
          savedAt: '2024-01-15T10:30:00Z',
          tags: ['ai', 'machine-learning', 'neural-networks'],
          author: 'Dr. Sarah Chen'
        },
        {
          id: '2',
          title: 'Graph Traversal Algorithms',
          type: 'snippet',
          description: 'BFS and DFS implementation examples',
          savedAt: '2024-01-14T15:45:00Z',
          tags: ['algorithms', 'graphs', 'data-structures']
        },
        {
          id: '3',
          title: 'Best Practices for API Design',
          type: 'resource',
          description: 'RESTful API design guidelines and patterns',
          savedAt: '2024-01-13T09:20:00Z',
          tags: ['api', 'backend', 'design']
        },
        {
          id: '4',
          title: 'Understanding Transformer Architecture',
          type: 'discussion',
          description: 'Discussion thread about attention mechanisms',
          savedAt: '2024-01-12T14:00:00Z',
          tags: ['ai', 'transformers', 'nlp'],
          author: 'Community Discussion'
        },
        {
          id: '5',
          title: 'React Hooks Deep Dive',
          type: 'lesson',
          description: 'Mastering useState, useEffect, and custom hooks',
          savedAt: '2024-01-11T11:30:00Z',
          tags: ['react', 'javascript', 'frontend'],
          author: 'John Developer'
        },
        {
          id: '6',
          title: 'Database Optimization Techniques',
          type: 'resource',
          description: 'Query optimization and indexing strategies',
          savedAt: '2024-01-10T16:15:00Z',
          tags: ['database', 'performance', 'sql']
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const removeFromLibrary = async (contentId: string) => {
    try {
      await ApiService.removeSavedContent(contentId);
      setSavedContent(prev => prev.filter(item => item.id !== contentId));
    } catch (error) {
      console.error('Error removing content:', error);
    }
  };

  const filteredContent = savedContent.filter(item => {
    const matchesFilter = filter === 'all' || item.type === filter;
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'lesson': return '📚';
      case 'snippet': return '💻';
      case 'discussion': return '💬';
      case 'resource': return '📄';
      default: return '📁';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="saved-content-library">
        <div className="library-loading">
          <div className="loading-spinner"></div>
          <p>Loading your saved content...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="saved-content-library">
      <div className="library-header">
        <div className="header-title">
          <h2>Saved Content Library</h2>
          <p>{savedContent.length} items saved</p>
        </div>
        <div className="header-actions">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search saved content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <span className="search-icon">🔍</span>
          </div>
          <div className="view-toggle">
            <button
              className={viewMode === 'grid' ? 'active' : ''}
              onClick={() => setViewMode('grid')}
              title="Grid View"
            >
              ▦
            </button>
            <button
              className={viewMode === 'list' ? 'active' : ''}
              onClick={() => setViewMode('list')}
              title="List View"
            >
              ☰
            </button>
          </div>
        </div>
      </div>

      <div className="library-filters">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All ({savedContent.length})
        </button>
        <button
          className={filter === 'lesson' ? 'active' : ''}
          onClick={() => setFilter('lesson')}
        >
          Lessons ({savedContent.filter(i => i.type === 'lesson').length})
        </button>
        <button
          className={filter === 'snippet' ? 'active' : ''}
          onClick={() => setFilter('snippet')}
        >
          Snippets ({savedContent.filter(i => i.type === 'snippet').length})
        </button>
        <button
          className={filter === 'discussion' ? 'active' : ''}
          onClick={() => setFilter('discussion')}
        >
          Discussions ({savedContent.filter(i => i.type === 'discussion').length})
        </button>
        <button
          className={filter === 'resource' ? 'active' : ''}
          onClick={() => setFilter('resource')}
        >
          Resources ({savedContent.filter(i => i.type === 'resource').length})
        </button>
      </div>

      {filteredContent.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📚</div>
          <h3>No saved content found</h3>
          <p>
            {searchQuery
              ? `No items match "${searchQuery}"`
              : `Start saving content to build your library`}
          </p>
          {searchQuery && (
            <button className="clear-search" onClick={() => setSearchQuery('')}>
              Clear Search
            </button>
          )}
        </div>
      ) : (
        <div className={`library-content ${viewMode}`}>
          {filteredContent.map(item => (
            <div
              key={item.id}
              className="content-card"
              onClick={() => setSelectedContent(item)}
            >
              <div className="card-header">
                <span className="type-badge">{getTypeIcon(item.type)} {item.type}</span>
                <button
                  className="remove-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFromLibrary(item.id);
                  }}
                  title="Remove from library"
                >
                  ✕
                </button>
              </div>
              <div className="card-body">
                <h3>{item.title}</h3>
                <p className="description">{item.description}</p>
                {item.author && (
                  <p className="author">By {item.author}</p>
                )}
              </div>
              <div className="card-footer">
                <div className="tags">
                  {item.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="tag">#{tag}</span>
                  ))}
                </div>
                <span className="saved-date">Saved {formatDate(item.savedAt)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedContent && (
        <div className="content-modal-overlay" onClick={() => setSelectedContent(null)}>
          <div className="content-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span className="type-badge">{getTypeIcon(selectedContent.type)} {selectedContent.type}</span>
              <button className="close-btn" onClick={() => setSelectedContent(null)}>✕</button>
            </div>
            <div className="modal-body">
              <h2>{selectedContent.title}</h2>
              <p className="modal-description">{selectedContent.description}</p>
              {selectedContent.author && (
                <p className="modal-author">By {selectedContent.author}</p>
              )}
              <div className="modal-tags">
                {selectedContent.tags.map(tag => (
                  <span key={tag} className="tag">#{tag}</span>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-primary">Open Content</button>
              <button
                className="btn-secondary"
                onClick={() => {
                  removeFromLibrary(selectedContent.id);
                  setSelectedContent(null);
                }}
              >
                Remove from Library
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedContentLibrary;
