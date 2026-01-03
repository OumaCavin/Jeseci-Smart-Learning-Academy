/**
 * Study Groups Components
 * 
 * Components for study groups with shared workspaces, notes, goals, and chat
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  Plus,
  Search,
  MessageSquare,
  Target,
  BookOpen,
  Calendar,
  MoreVertical,
  ChevronRight,
  Settings,
  UserPlus,
  Trophy,
  Clock,
  Star,
  Send,
  Edit3,
  Trash2,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';
import advancedCollaborationService, {
  StudyGroup,
  StudyGroupNote,
  StudyGroupGoal,
  StudyGroupMessage
} from '../../services/advancedCollaborationService';

// Props interfaces
interface StudyGroupListProps {
  onGroupSelect?: (group: StudyGroup) => void;
}

interface StudyGroupDetailProps {
  groupId: string;
  onBack?: () => void;
}

interface StudyGroupNotesProps {
  groupId: string;
}

interface StudyGroupGoalsProps {
  groupId: string;
}

interface StudyGroupChatProps {
  groupId: string;
}

// Study Groups List Component
export const StudyGroupList: React.FC<StudyGroupListProps> = ({ onGroupSelect }) => {
  const [groups, setGroups] = useState<StudyGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState<string | undefined>();
  const [showCreateModal, setShowCreateModal] = useState(false);

  const loadGroups = useCallback(async () => {
    try {
      setLoading(true);
      const result = await advancedCollaborationService.getStudyGroups({ topic: selectedTopic });
      if (result.success && result.data) {
        setGroups(result.data);
      }
    } catch (error) {
      console.error('Error loading study groups:', error);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedTopic]);

  useEffect(() => {
    loadGroups();
  }, [loadGroups]);

  const topics = ['All Topics', 'Jac Programming', 'Object-Spatial Programming', 'Web Development', 'Data Science'];

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="rounded-full bg-gray-200 h-12 w-12"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search study groups..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex gap-2">
            {topics.map((topic) => (
              <button
                key={topic}
                onClick={() => setSelectedTopic(topic === 'All Topics' ? undefined : topic)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  (topic === 'All Topics' && !selectedTopic) ||
                  (topic !== 'All Topics' && selectedTopic === topic)
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {topic}
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Group
          </button>
        </div>
      </div>

      {/* Groups List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="divide-y divide-gray-100">
          {groups.length === 0 ? (
            <div className="p-8 text-center">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No study groups found</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Create the First Group
              </button>
            </div>
          ) : (
            groups.map((group) => (
              <div
                key={group.group_id}
                onClick={() => onGroupSelect?.(group)}
                className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
                      {group.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{group.name}</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">{group.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {group.member_count}/{group.max_members} members
                        </span>
                        <span className="flex items-center gap-1">
                          <Target className="w-4 h-4" />
                          {group.target_topic}
                        </span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Study Group Notes Component
export const StudyGroupNotes: React.FC<StudyGroupNotesProps> = ({ groupId }) => {
  const [notes, setNotes] = useState<StudyGroupNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditor, setShowEditor] = useState(false);
  const [newNote, setNewNote] = useState({ title: '', content: '' });

  const loadNotes = useCallback(async () => {
    try {
      setLoading(true);
      const result = await advancedCollaborationService.getGroupNotes(groupId);
      if (result.success && result.data) {
        setNotes(result.data);
      }
    } catch (error) {
      console.error('Error loading notes:', error);
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    loadNotes();
  }, [loadNotes]);

  const handleCreateNote = async () => {
    if (!newNote.title.trim() || !newNote.content.trim()) return;

    try {
      await advancedCollaborationService.createGroupNote(groupId, newNote.title, newNote.content);
      setShowEditor(false);
      setNewNote({ title: '', content: '' });
      loadNotes();
    } catch (error) {
      console.error('Error creating note:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-500" />
          Group Notes
        </h3>
        <button
          onClick={() => setShowEditor(true)}
          className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Note
        </button>
      </div>

      {showEditor && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <input
            type="text"
            placeholder="Note title..."
            value={newNote.title}
            onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3"
          />
          <textarea
            placeholder="Write your note content..."
            value={newNote.content}
            onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3"
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowEditor(false)}
              className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateNote}
              className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Save Note
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {notes.map((note) => (
          <div key={note.note_id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-semibold text-gray-900">{note.title}</h4>
              {note.is_pinned && (
                <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">Pinned</span>
              )}
            </div>
            <p className="text-gray-600 text-sm line-clamp-3">{note.content}</p>
            <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
              <span>{note.author_name}</span>
              <span>{new Date(note.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Study Group Goals Component
export const StudyGroupGoals: React.FC<StudyGroupGoalsProps> = ({ groupId }) => {
  const [goals, setGoals] = useState<StudyGroupGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newGoal, setNewGoal] = useState({ title: '', description: '', targetDate: '' });

  const loadGoals = useCallback(async () => {
    try {
      setLoading(true);
      const result = await advancedCollaborationService.getGroupGoals(groupId);
      if (result.success && result.data) {
        setGoals(result.data);
      }
    } catch (error) {
      console.error('Error loading goals:', error);
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    loadGoals();
  }, [loadGoals]);

  const handleCreateGoal = async () => {
    if (!newGoal.title.trim()) return;

    try {
      await advancedCollaborationService.createGroupGoal(groupId, newGoal.title, {
        description: newGoal.description,
        targetCompletionDate: newGoal.targetDate
      });
      setShowForm(false);
      setNewGoal({ title: '', description: '', targetDate: '' });
      loadGoals();
    } catch (error) {
      console.error('Error creating goal:', error);
    }
  };

  const handleCompleteGoal = async (goalId: string) => {
    try {
      await advancedCollaborationService.completeGroupGoal(groupId, goalId);
      loadGoals();
    } catch (error) {
      console.error('Error completing goal:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Target className="w-5 h-5 text-green-500" />
          Group Goals
        </h3>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Goal
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <input
            type="text"
            placeholder="Goal title..."
            value={newGoal.title}
            onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3"
          />
          <textarea
            placeholder="Goal description..."
            value={newGoal.description}
            onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3"
          />
          <input
            type="date"
            value={newGoal.targetDate}
            onChange={(e) => setNewGoal({ ...newGoal, targetDate: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3"
          />
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowForm(false)} className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded-lg">
              Cancel
            </button>
            <button onClick={handleCreateGoal} className="px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600">
              Create Goal
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {goals.map((goal) => (
          <div
            key={goal.goal_id}
            className={`bg-white rounded-xl shadow-sm border p-4 ${
              goal.is_completed ? 'border-green-200 bg-green-50' : 'border-gray-100'
            }`}
          >
            <div className="flex items-start gap-3">
              <button
                onClick={() => !goal.is_completed && handleCompleteGoal(goal.goal_id)}
                disabled={goal.is_completed}
                className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                  goal.is_completed
                    ? 'bg-green-500 border-green-500 text-white'
                    : 'border-gray-300 hover:border-green-500'
                }`}
              >
                {goal.is_completed && <CheckCircle className="w-4 h-4" />}
              </button>
              <div className="flex-1">
                <h4 className={`font-semibold ${goal.is_completed ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                  {goal.title}
                </h4>
                {goal.description && (
                  <p className="text-sm text-gray-600 mt-1">{goal.description}</p>
                )}
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Due: {goal.target_completion_date ? new Date(goal.target_completion_date).toLocaleDateString() : 'No date'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main StudyGroups Component
const StudyGroups: React.FC = () => {
  const [selectedGroup, setSelectedGroup] = useState<StudyGroup | null>(null);
  const [activeView, setActiveView] = useState<'list' | 'notes' | 'goals'>('list');

  return (
    <div className="space-y-6">
      {selectedGroup ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <button
            onClick={() => {
              setSelectedGroup(null);
              setActiveView('list');
            }}
            className="text-blue-500 hover:text-blue-600 mb-4"
          >
            ← Back to Groups
          </button>

          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
              {selectedGroup.name.charAt(0)}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{selectedGroup.name}</h2>
              <p className="text-gray-600">{selectedGroup.learning_goal}</p>
            </div>
          </div>

          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setActiveView('notes')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeView === 'notes' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <BookOpen className="w-4 h-4 inline-block mr-2" />
              Notes
            </button>
            <button
              onClick={() => setActiveView('goals')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeView === 'goals' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Target className="w-4 h-4 inline-block mr-2" />
              Goals
            </button>
          </div>

          {activeView === 'notes' && <StudyGroupNotes groupId={selectedGroup.group_id} />}
          {activeView === 'goals' && <StudyGroupGoals groupId={selectedGroup.group_id} />}
        </div>
      ) : (
        <StudyGroupList onGroupSelect={(group) => setSelectedGroup(group)} />
      )}
    </div>
  );
};

export default StudyGroups;
