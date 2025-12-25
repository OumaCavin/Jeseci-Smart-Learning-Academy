#!/usr/bin/env python3
"""
System Core Module - Enhanced Features
Jeseci Smart Learning Academy - Phase 4 Enterprise Intelligence

This module provides enhanced system capabilities:
- Content versioning with history and rollback
- Advanced search functionality
- Multi-language support (i18n)
- Content management enhancements
- System utilities and utilities

Author: Cavin Otieno
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import re
import hashlib
from collections import defaultdict

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel, Field
from admin_auth import get_current_admin_user, AdminRole

# Initialize router
system_router = APIRouter()

# =============================================================================
# Data Models
# =============================================================================

class ContentType(str, Enum):
    """Content types for versioning and search"""
    COURSE = "course"
    LESSON = "lesson"
    QUIZ = "quiz"
    CONCEPT = "concept"
    LEARNING_PATH = "learning_path"
    ASSESSMENT = "assessment"

@dataclass
class ContentVersion:
    """Version snapshot of content"""
    version_id: str
    content_id: str
    content_type: ContentType
    version_number: int
    title: str
    content_data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_by: str
    created_at: datetime
    change_summary: str
    diff_hash: str

@dataclass
class ContentHistory:
    """Content version history"""
    content_id: str
    content_type: ContentType
    current_version: int
    versions: List[ContentVersion]
    created_at: datetime
    updated_at: datetime

@dataclass
class SearchResult:
    """Search result item"""
    result_id: str
    content_type: str
    content_id: str
    title: str
    snippet: str
    highlights: List[str]
    score: float
    matched_fields: List[str]
    metadata: Dict[str, Any]

@dataclass
class SearchQuery:
    """Advanced search query"""
    query_id: str
    search_terms: str
    filters: Dict[str, Any]
    sort_order: str
    page: int
    per_page: int
    created_at: datetime

# =============================================================================
# Internationalization (i18n)
# =============================================================================

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native_name": "English", "rtl": False, "default": True},
    "es": {"name": "Spanish", "native_name": "Español", "rtl": False, "default": False},
    "fr": {"name": "French", "native_name": "Français", "rtl": False, "default": False},
    "de": {"name": "German", "native_name": "Deutsch", "rtl": False, "default": False},
    "zh": {"name": "Chinese", "native_name": "中文", "rtl": False, "default": False},
    "ja": {"name": "Japanese", "native_name": "日本語", "rtl": False, "default": False},
    "ar": {"name": "Arabic", "native_name": "العربية", "rtl": True, "default": False},
    "pt": {"name": "Portuguese", "native_name": "Português", "rtl": False, "default": False},
    "ko": {"name": "Korean", "native_name": "한국어", "rtl": False, "default": False}
}

# Translation strings
TRANSLATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "en": {
        "common": {
            "loading": "Loading...",
            "save": "Save",
            "cancel": "Cancel",
            "delete": "Delete",
            "edit": "Edit",
            "view": "View",
            "search": "Search",
            "filter": "Filter",
            "export": "Export",
            "import": "Import"
        },
        "admin": {
            "dashboard": "Dashboard",
            "users": "User Management",
            "content": "Content Management",
            "analytics": "Analytics",
            "settings": "Settings",
            "logout": "Logout"
        },
        "content": {
            "course": "Course",
            "lesson": "Lesson",
            "quiz": "Quiz",
            "concept": "Concept",
            "path": "Learning Path"
        },
        "actions": {
            "create": "Create New",
            "update": "Update",
            "delete_confirm": "Are you sure you want to delete this item?",
            "rollback": "Rollback to Version",
            "version_history": "Version History"
        }
    },
    "es": {
        "common": {
            "loading": "Cargando...",
            "save": "Guardar",
            "cancel": "Cancelar",
            "delete": "Eliminar",
            "edit": "Editar",
            "view": "Ver",
            "search": "Buscar",
            "filter": "Filtrar",
            "export": "Exportar",
            "import": "Importar"
        },
        "admin": {
            "dashboard": "Panel de Control",
            "users": "Gestión de Usuarios",
            "content": "Gestión de Contenido",
            "analytics": "Analíticas",
            "settings": "Configuración",
            "logout": "Cerrar Sesión"
        },
        "content": {
            "course": "Curso",
            "lesson": "Lección",
            "quiz": "Cuestionario",
            "concept": "Concepto",
            "path": "Ruta de Aprendizaje"
        },
        "actions": {
            "create": "Crear Nuevo",
            "update": "Actualizar",
            "delete_confirm": "¿Está seguro de que desea eliminar este elemento?",
            "rollback": "Revertir a Versión",
            "version_history": "Historial de Versiones"
        }
    },
    "fr": {
        "common": {
            "loading": "Chargement...",
            "save": "Enregistrer",
            "cancel": "Annuler",
            "delete": "Supprimer",
            "edit": "Modifier",
            "view": "Voir",
            "search": "Rechercher",
            "filter": "Filtrer",
            "export": "Exporter",
            "import": "Importer"
        },
        "admin": {
            "dashboard": "Tableau de Bord",
            "users": "Gestion des Utilisateurs",
            "content": "Gestion du Contenu",
            "analytics": "Analytique",
            "settings": "Paramètres",
            "logout": "Déconnexion"
        },
        "content": {
            "course": "Cours",
            "lesson": "Leçon",
            "quiz": "Quiz",
            "concept": "Concept",
            "path": "Parcours d'Apprentissage"
        },
        "actions": {
            "create": "Créer Nouveau",
            "update": "Mettre à jour",
            "delete_confirm": "Êtes-vous sûr de vouloir supprimer cet élément?",
            "rollback": "Revenir à la Version",
            "version_history": "Historique des Versions"
        }
    },
    "de": {
        "common": {
            "loading": "Laden...",
            "save": "Speichern",
            "cancel": "Abbrechen",
            "delete": "Löschen",
            "edit": "Bearbeiten",
            "view": "Ansehen",
            "search": "Suchen",
            "filter": "Filtern",
            "export": "Exportieren",
            "import": "Importieren"
        },
        "admin": {
            "dashboard": "Dashboard",
            "users": "Benutzerverwaltung",
            "content": "Inhaltsverwaltung",
            "analytics": "Analytik",
            "settings": "Einstellungen",
            "logout": "Abmelden"
        },
        "content": {
            "course": "Kurs",
            "lesson": "Lektion",
            "quiz": "Quiz",
            "concept": "Konzept",
            "path": "Lernpfad"
        },
        "actions": {
            "create": "Neu Erstellen",
            "update": "Aktualisieren",
            "delete_confirm": "Möchten Sie diesen Eintrag wirklich löschen?",
            "rollback": "Zurück zur Version",
            "version_history": "Versionshistorie"
        }
    }
}

# =============================================================================
# In-Memory Data Store
# =============================================================================

# Content version history
content_history: Dict[str, ContentHistory] = {}

# Search index
search_index: Dict[str, List[str]] = {
    "courses": [],
    "lessons": [],
    "quizzes": [],
    "concepts": [],
    "learning_paths": [],
    "users": []
}

# Indexed documents for search
indexed_documents: Dict[str, Dict[str, Any]] = {}

# Search history
search_history: List[SearchQuery] = []

# Initialize with sample data
def initialize_system_data():
    """Initialize sample content for demonstration"""
    # Sample content with versions
    sample_contents = [
        {
            "content_id": "course_jac_101",
            "content_type": ContentType.COURSE,
            "title": "Jaclang Programming Fundamentals",
            "versions": 3
        },
        {
            "content_id": "quiz_jac_basics",
            "content_type": ContentType.QUIZ,
            "title": "Jaclang Basics Assessment",
            "versions": 5
        },
        {
            "content_id": "concept_osp",
            "content_type": ContentType.CONCEPT,
            "title": "Object-Spatial Programming",
            "versions": 2
        }
    ]
    
    for content in sample_contents:
        versions = []
        for v in range(1, content["versions"] + 1):
            version = ContentVersion(
                version_id=f"{content['content_id']}_v{v}",
                content_id=content["content_id"],
                content_type=content["content_type"],
                version_number=v,
                title=content["title"],
                content_data={
                    "description": f"Version {v} of {content['title']}",
                    "modules": ["module_1", "module_2"],
                    "duration": "4 weeks"
                },
                metadata={"word_count": 500 + v * 50},
                created_by="admin",
                created_at=datetime.now(),
                change_summary=f"Updated content for version {v}",
                diff_hash=hashlib.md5(f"content_{content['content_id']}_v{v}".encode()).hexdigest()
            )
            versions.append(version)
        
        history = ContentHistory(
            content_id=content["content_id"],
            content_type=content["content_type"],
            current_version=content["versions"],
            versions=versions,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        content_history[content["content_id"]] = history
    
    # Sample search index
    sample_courses = [
        {
            "id": "course_jac_101",
            "title": "Jaclang Programming Fundamentals",
            "description": "Learn Jaclang from scratch with hands-on graph-based projects",
            "content_type": "course",
            "tags": ["jaclang", "programming", "beginner", "osp"],
            "author": "Dr. Smith",
            "created_at": "2025-01-15T10:00:00Z"
        },
        {
            "id": "course_jac_nodes",
            "title": "Nodes and Edges Mastery",
            "description": "Master graph structures with Jaclang nodes and edge relationships",
            "content_type": "course",
            "tags": ["jaclang", "nodes", "edges", "graph"],
            "author": "Prof. Johnson",
            "created_at": "2025-02-20T14:30:00Z"
        },
        {
            "id": "course_jac_walkers",
            "title": "Advanced Walker Patterns",
            "description": "Deep dive into walker design patterns for complex graph traversal",
            "content_type": "course",
            "tags": ["jaclang", "walkers", "traversal", "patterns"],
            "author": "Dr. Chen",
            "created_at": "2025-03-10T09:15:00Z"
        }
    ]

    for course in sample_courses:
        indexed_documents[course["id"]] = course
        search_index["courses"].append(course["id"])

    # Sample quizzes
    sample_quizzes = [
        {
            "id": "quiz_jac_basics",
            "title": "Jaclang Basics Assessment",
            "description": "Test your understanding of Jaclang fundamentals",
            "content_type": "quiz",
            "tags": ["jaclang", "assessment", "fundamentals", "nodes"],
            "author": "Dr. Smith",
            "created_at": "2025-01-20T11:00:00Z"
        },
        {
            "id": "quiz_jac_walkers",
            "title": "Walker Traversal Quiz",
            "description": "Evaluate your walker navigation and graph traversal knowledge",
            "content_type": "quiz",
            "tags": ["jaclang", "walkers", "graph", "assessment"],
            "author": "Prof. Johnson",
            "created_at": "2025-02-25T16:00:00Z"
        }
    ]

    for quiz in sample_quizzes:
        indexed_documents[quiz["id"]] = quiz
        search_index["quizzes"].append(quiz["id"])

initialize_system_data()

# =============================================================================
# Request/Response Models
# =============================================================================

class ContentVersionRequest(BaseModel):
    """Request model for creating content version"""
    content_id: str
    content_type: ContentType
    title: str
    content_data: Dict[str, Any]
    change_summary: str = Field(default="Content update")

class VersionResponse(BaseModel):
    """Response model for version operations"""
    success: bool
    version: Dict[str, Any]
    history: Dict[str, Any]

class RollbackRequest(BaseModel):
    """Request model for rollback operation"""
    target_version: int

class RollbackResponse(BaseModel):
    """Response model for rollback operation"""
    success: bool
    message: str
    current_version: int
    rolled_back_to: int
    new_version: Dict[str, Any]

class SearchRequest(BaseModel):
    """Request model for advanced search"""
    query: str = Field(..., min_length=1, max_length=500)
    content_types: List[str] = Field(default=["course", "lesson", "quiz", "concept", "learning_path"])
    filters: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort_by: str = Field(default="relevance", pattern="^(relevance|date|title|score)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

class SearchResponse(BaseModel):
    """Response model for search operations"""
    success: bool
    query: str
    results: List[Dict[str, Any]]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    facets: Dict[str, Any]
    search_time_ms: float

class TranslationRequest(BaseModel):
    """Request model for translations"""
    key: str
    namespace: str = "common"
    target_language: str

class TranslationResponse(BaseModel):
    """Response model for translations"""
    success: bool
    original_key: str
    translated_value: str
    language: str

class LanguageDetectionRequest(BaseModel):
    """Request model for language detection"""
    text: str = Field(..., min_length=10, max_length=5000)

# =============================================================================
# Version Control Functions
# =============================================================================

def create_diff_hash(content_data: Dict[str, Any]) -> str:
    """Create hash of content data for comparison"""
    content_str = json.dumps(content_data, sort_keys=True)
    return hashlib.md5(content_str.encode()).hexdigest()

def calculate_diff(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate differences between two content versions"""
    diff = {
        "added": [],
        "removed": [],
        "modified": [],
        "unchanged": []
    }
    
    all_keys = set(old_data.keys()) | set(new_data.keys())
    
    for key in all_keys:
        old_val = old_data.get(key)
        new_val = new_data.get(key)
        
        if key not in old_data:
            diff["added"].append(key)
        elif key not in new_data:
            diff["removed"].append(key)
        elif old_val != new_val:
            diff["modified"].append(key)
        else:
            diff["unchanged"].append(key)
    
    return diff

# =============================================================================
# Search Functions
# =============================================================================

def calculate_relevance_score(doc: Dict[str, Any], query: str) -> float:
    """Calculate relevance score for search result"""
    query_terms = query.lower().split()
    title = doc.get("title", "").lower()
    description = doc.get("description", "").lower()
    tags = [t.lower() for t in doc.get("tags", [])]
    
    score = 0.0
    
    # Title matches (highest weight)
    for term in query_terms:
        if term in title:
            score += 10.0
            if title.startswith(term):
                score += 5.0
    
    # Description matches (medium weight)
    for term in query_terms:
        if term in description:
            score += 3.0
    
    # Tag matches (medium weight)
    for term in query_terms:
        if term in tags:
            score += 5.0
    
    return score

def highlight_text(text: str, query: str) -> str:
    """Add highlighting to matched text"""
    query_terms = query.lower().split()
    highlighted = text
    
    for term in query_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        highlighted = pattern.sub(f"**{term.upper()}**", highlighted)
    
    return highlighted

def parse_search_query(query: str) -> Dict[str, Any]:
    """Parse search query for advanced operators"""
    parsed = {
        "terms": [],
        "exact_phrases": [],
        "excluded_terms": []
    }
    
    # Handle exact phrases
    exact_pattern = r'"([^"]+)"'
    exact_matches = re.findall(exact_pattern, query)
    for phrase in exact_matches:
        query = query.replace(f'"{phrase}"', '')
        parsed["exact_phrases"].append(phrase)
    
    # Handle exclusions
    words = query.split()
    for word in words:
        if word.startswith('-'):
            parsed["excluded_terms"].append(word[1:])
        else:
            parsed["terms"].append(word)
    
    return parsed

# =============================================================================
# API Endpoints - Content Versioning
# =============================================================================

@system_router.post("/content/version", response_model=VersionResponse)
async def create_content_version(
    request: ContentVersionRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Create a new version of content.
    
    This endpoint saves the current state of content as a new version,
    maintaining a complete history of changes.
    """
    content_id = request.content_id
    
    # Get or create history
    if content_id in content_history:
        history = content_history[content_id]
        new_version_number = history.current_version + 1
    else:
        history = ContentHistory(
            content_id=content_id,
            content_type=request.content_type,
            current_version=0,
            versions=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        new_version_number = 1
    
    # Create new version
    version = ContentVersion(
        version_id=f"{content_id}_v{new_version_number}",
        content_id=content_id,
        content_type=request.content_type,
        version_number=new_version_number,
        title=request.title,
        content_data=request.content_data,
        metadata={"word_count": len(json.dumps(request.content_data))},
        created_by=current_user.get("username", "unknown"),
        created_at=datetime.now(),
        change_summary=request.change_summary,
        diff_hash=create_diff_hash(request.content_data)
    )
    
    # Update history
    history.versions.append(version)
    history.current_version = new_version_number
    history.updated_at = datetime.now()
    
    content_history[content_id] = history
    
    return VersionResponse(
        success=True,
        version={
            "version_id": version.version_id,
            "content_id": version.content_id,
            "version_number": version.version_number,
            "title": version.title,
            "created_by": version.created_by,
            "created_at": version.created_at.isoformat(),
            "change_summary": version.change_summary,
            "diff_hash": version.diff_hash
        },
        history={
            "content_id": history.content_id,
            "current_version": history.current_version,
            "total_versions": len(history.versions),
            "created_at": history.created_at.isoformat(),
            "updated_at": history.updated_at.isoformat()
        }
    )

@system_router.get("/content/{content_id}/history")
async def get_content_history(
    content_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=50),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get version history for a piece of content.
    
    Returns all versions with pagination support.
    """
    if content_id not in content_history:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Content history not found"}
        )
    
    history = content_history[content_id]
    versions = history.versions[::-1]  # Reverse for newest first
    
    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated_versions = versions[start:end]
    
    return {
        "success": True,
        "content_id": content_id,
        "content_type": history.content_type.value,
        "current_version": history.current_version,
        "versions": [
            {
                "version_id": v.version_id,
                "version_number": v.version_number,
                "title": v.title,
                "created_by": v.created_by,
                "created_at": v.created_at.isoformat(),
                "change_summary": v.change_summary,
                "diff_hash": v.diff_hash
            }
            for v in paginated_versions
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_versions": len(versions),
            "total_pages": (len(versions) + per_page - 1) // per_page
        }
    }

@system_router.get("/content/{content_id}/versions/{version_number}")
async def get_specific_version(
    content_id: str,
    version_number: int,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get a specific version of content.
    """
    if content_id not in content_history:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Content history not found"}
        )
    
    history = content_history[content_id]
    
    version = next(
        (v for v in history.versions if v.version_number == version_number),
        None
    )
    
    if not version:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Version not found"}
        )
    
    # Calculate diff with current version
    if version_number != history.current_version:
        current_version = next(
            v for v in history.versions if v.version_number == history.current_version
        )
        diff = calculate_diff(version.content_data, current_version.content_data)
    else:
        diff = None
    
    return {
        "success": True,
        "version": {
            "version_id": version.version_id,
            "content_id": version.content_id,
            "version_number": version.version_number,
            "title": version.title,
            "content_data": version.content_data,
            "metadata": version.metadata,
            "created_by": version.created_by,
            "created_at": version.created_at.isoformat(),
            "change_summary": version.change_summary,
            "diff_hash": version.diff_hash
        },
        "diff_with_current": diff
    }

@system_router.post("/content/{content_id}/rollback", response_model=RollbackResponse)
async def rollback_to_version(
    content_id: str,
    request: RollbackRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Rollback content to a specific version.
    
    Creates a new version with the content from the target version.
    """
    if content_id not in content_history:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Content history not found"}
        )
    
    history = content_history[content_id]
    
    # Find target version
    target_version = next(
        (v for v in history.versions if v.version_number == request.target_version),
        None
    )
    
    if not target_version:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Target version not found"}
        )
    
    # Create new version with target content
    new_version_number = history.current_version + 1
    new_version = ContentVersion(
        version_id=f"{content_id}_v{new_version_number}",
        content_id=content_id,
        content_type=history.content_type,
        version_number=new_version_number,
        title=target_version.title,
        content_data=target_version.content_data,
        metadata={"word_count": target_version.metadata.get("word_count", 0)},
        created_by=current_user.get("username", "unknown"),
        created_at=datetime.now(),
        change_summary=f"Rollback to version {request.target_version}",
        diff_hash=target_version.diff_hash
    )
    
    # Update history
    history.versions.append(new_version)
    history.current_version = new_version_number
    history.updated_at = datetime.now()
    
    return RollbackResponse(
        success=True,
        message=f"Successfully rolled back to version {request.target_version}",
        current_version=history.current_version,
        rolled_back_to=request.target_version,
        new_version={
            "version_id": new_version.version_id,
            "version_number": new_version.version_number,
            "created_at": new_version.created_at.isoformat(),
            "change_summary": new_version.change_summary
        }
    )

@system_router.get("/content/{content_id}/compare")
async def compare_versions(
    content_id: str,
    version_a: int = Query(..., ge=1),
    version_b: int = Query(..., ge=1),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Compare two versions of content side by side.
    """
    if content_id not in content_history:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Content history not found"}
        )
    
    history = content_history[content_id]
    
    version1 = next(
        (v for v in history.versions if v.version_number == version_a),
        None
    )
    version2 = next(
        (v for v in history.versions if v.version_number == version_b),
        None
    )
    
    if not version1 or not version2:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "One or both versions not found"}
        )
    
    diff = calculate_diff(version1.content_data, version2.content_data)
    
    return {
        "success": True,
        "comparison": {
            "version_a": {
                "version_number": version_a,
                "created_at": version1.created_at.isoformat(),
                "created_by": version1.created_by
            },
            "version_b": {
                "version_number": version_b,
                "created_at": version2.created_at.isoformat(),
                "created_by": version2.created_by
            },
            "diff": diff,
            "content_a": version1.content_data,
            "content_b": version2.content_data
        }
    }

# =============================================================================
# API Endpoints - Advanced Search
# =============================================================================

@system_router.post("/search/global", response_model=SearchResponse)
async def global_search(
    request: SearchRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Perform advanced global search across all content types.
    
    Supports:
    - Full-text search with relevance scoring
    - Content type filtering
    - Tag filtering
    - Author filtering
    - Date range filtering
    - Multiple sort options
    """
    import time
    start_time = time.time()
    
    # Parse and expand query
    parsed_query = parse_search_query(request.query)
    all_terms = parsed_query["terms"] + parsed_query["exact_phrases"]
    
    # Collect candidate documents
    candidates = []
    
    for content_type in request.content_types:
        index_key = content_type + "s" if not content_type.endswith("s") else content_type
        if index_key in search_index:
            for doc_id in search_index[index_key]:
                if doc_id in indexed_documents:
                    doc = indexed_documents[doc_id]
                    
                    # Apply filters
                    # Tag filter
                    if request.tags:
                        if not any(tag in doc.get("tags", []) for tag in request.tags):
                            continue
                    
                    # Author filter
                    if request.author and doc.get("author") != request.author:
                        continue
                    
                    # Date range filter
                    doc_date = datetime.fromisoformat(doc.get("created_at", "2025-01-01"))
                    if request.date_from and doc_date < datetime.fromisoformat(request.date_from):
                        continue
                    if request.date_to and doc_date > datetime.fromisoformat(request.date_to):
                        continue
                    
                    candidates.append(doc)
    
    # Calculate relevance scores
    scored_results = []
    for doc in candidates:
        # Calculate base relevance
        base_score = calculate_relevance_score(doc, request.query)
        
        # Apply exact phrase bonus
        for phrase in parsed_query["exact_phrases"]:
            if phrase.lower() in doc.get("title", "").lower():
                base_score += 15.0
            if phrase.lower() in doc.get("description", "").lower():
                base_score += 10.0
        
        # Apply exclusion penalty
        for term in parsed_query["excluded_terms"]:
            if term in doc.get("title", "").lower() or term in doc.get("description", "").lower():
                base_score = 0
                break
        
        if base_score > 0:
            matched_fields = []
            doc_text = (doc.get("title", "") + " " + doc.get("description", "")).lower()
            for term in all_terms:
                if term in doc.get("title", "").lower():
                    matched_fields.append("title")
                if term in doc.get("description", "").lower():
                    matched_fields.append("description")
            
            scored_results.append({
                "document": doc,
                "score": base_score,
                "matched_fields": list(set(matched_fields))
            })
    
    # Sort results
    if request.sort_by == "date":
        scored_results.sort(
            key=lambda x: x["document"].get("created_at", ""),
            reverse=True
        )
    elif request.sort_by == "title":
        scored_results.sort(
            key=lambda x: x["document"].get("title", ""),
            reverse=False
        )
    elif request.sort_by == "score":
        scored_results.sort(key=lambda x: x["score"], reverse=True)
    else:  # relevance (default)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Calculate facets
    facets = {
        "content_types": {},
        "authors": {},
        "tags": {}
    }
    
    for result in scored_results:
        doc = result["document"]
        # Content type facets
        ct = doc.get("content_type", "unknown")
        facets["content_types"][ct] = facets["content_types"].get(ct, 0) + 1
        # Author facets
        author = doc.get("author", "Unknown")
        facets["authors"][author] = facets["authors"].get(author, 0) + 1
        # Tag facets
        for tag in doc.get("tags", []):
            facets["tags"][tag] = facets["tags"].get(tag, 0) + 1
    
    # Paginate
    total_count = len(scored_results)
    total_pages = (total_count + request.per_page - 1) // request.per_page
    start_idx = (request.page - 1) * request.per_page
    paginated_results = scored_results[start_idx:start_idx + request.per_page]
    
    # Build response
    results = []
    for item in paginated_results:
        doc = item["document"]
        results.append({
            "result_id": doc["id"],
            "content_type": doc["content_type"],
            "content_id": doc["id"],
            "title": doc["title"],
            "snippet": highlight_text(doc.get("description", ""), request.query),
            "highlights": [highlight_text(doc.get("title", ""), request.query)],
            "score": round(item["score"], 2),
            "matched_fields": item["matched_fields"],
            "metadata": {
                "author": doc.get("author"),
                "created_at": doc.get("created_at"),
                "tags": doc.get("tags", [])
            }
        })
    
    # Record search query
    search_query = SearchQuery(
        query_id=str(uuid.uuid4()),
        search_terms=request.query,
        filters={
            "content_types": request.content_types,
            "tags": request.tags,
            "author": request.author
        },
        sort_order=request.sort_by,
        page=request.page,
        per_page=request.per_page,
        created_at=datetime.now()
    )
    search_history.append(search_query)
    
    search_time_ms = (time.time() - start_time) * 1000
    
    return SearchResponse(
        success=True,
        query=request.query,
        results=results,
        total_count=total_count,
        page=request.page,
        per_page=request.per_page,
        total_pages=total_pages,
        facets=facets,
        search_time_ms=round(search_time_ms, 2)
    )

@system_router.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(default=10, ge=1, le=20),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get search suggestions based on partial query.
    
    Returns matching titles and tags.
    """
    q_lower = q.lower()
    suggestions = {
        "titles": [],
        "tags": []
    }
    
    # Collect titles
    for doc in indexed_documents.values():
        title = doc.get("title", "")
        if q_lower in title.lower():
            suggestions["titles"].append({
                "id": doc["id"],
                "title": title,
                "type": doc["content_type"]
            })
    
    # Collect tags
    all_tags = set()
    for doc in indexed_documents.values():
        all_tags.update(doc.get("tags", []))
    
    for tag in all_tags:
        if q_lower in tag.lower():
            suggestions["tags"].append(tag)
    
    # Limit results
    suggestions["titles"] = suggestions["titles"][:limit]
    suggestions["tags"] = suggestions["tags"][:limit]
    
    return {
        "success": True,
        "query": q,
        "suggestions": suggestions,
        "timestamp": datetime.now().isoformat()
    }

@system_router.get("/search/history")
async def get_search_history(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get recent search history.
    """
    recent = search_history[-limit:][::-1] if search_history else []
    
    return {
        "success": True,
        "history": [
            {
                "query_id": q.query_id,
                "search_terms": q.search_terms,
                "filters": q.filters,
                "sort_order": q.sort_order,
                "page": q.page,
                "created_at": q.created_at.isoformat()
            }
            for q in recent
        ],
        "total": len(search_history)
    }

@system_router.post("/search/index")
async def reindex_content(
    content_type: Optional[str] = None,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Trigger content reindexing.
    
    In production, this would rebuild the search index from the database.
    """
    if current_user.get("admin_role") != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Only Super Admins can trigger reindexing"}
        )
    
    # In production: rebuild index from database
    indexed_count = len(indexed_documents)
    
    return {
        "success": True,
        "message": "Reindexing completed",
        "indexed_documents": indexed_count,
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# API Endpoints - Internationalization
# =============================================================================

@system_router.get("/i18n/languages")
async def get_supported_languages():
    """
    Get list of supported languages.
    """
    return {
        "success": True,
        "languages": [
            {
                "code": code,
                "name": info["name"],
                "native_name": info["native_name"],
                "rtl": info["rtl"],
                "default": info["default"]
            }
            for code, info in SUPPORTED_LANGUAGES.items()
        ]
    }

@system_router.get("/i18n/translate/{language}/{namespace}/{key}")
async def get_translation(
    language: str,
    namespace: str,
    key: str
):
    """
    Get translation for a specific key.
    
    Falls back to English if translation not found.
    """
    if language not in SUPPORTED_LANGUAGES:
        language = "en"
    
    # Try requested language
    translations = TRANSLATIONS.get(language, {})
    namespace_translations = translations.get(namespace, {})
    value = namespace_translations.get(key)
    
    # Fall back to English
    if not value:
        en_translations = TRANSLATIONS.get("en", {})
        en_namespace = en_translations.get(namespace, {})
        value = en_namespace.get(key, key)  # Return key if not found
    
    return {
        "success": True,
        "language": language,
        "namespace": namespace,
        "key": key,
        "translation": value
    }

@system_router.get("/i18n/bundle/{language}")
async def get_translation_bundle(
    language: str,
    namespaces: str = Query(default="common,admin,content,actions")
):
    """
    Get complete translation bundle for a language.
    
    Useful for frontend i18n initialization.
    """
    if language not in SUPPORTED_LANGUAGES:
        language = "en"
    
    requested_namespaces = [ns.strip() for ns in namespaces.split(",")]
    bundle = {}
    
    translations = TRANSLATIONS.get(language, {})
    for namespace in requested_namespaces:
        bundle[namespace] = translations.get(namespace, {})
    
    # Include English fallbacks for missing keys
    en_translations = TRANSLATIONS.get("en", {})
    for namespace in requested_namespaces:
        if namespace not in bundle:
            bundle[namespace] = en_translations.get(namespace, {})
        else:
            # Merge with English fallbacks
            en_ns = en_translations.get(namespace, {})
            for key, value in en_ns.items():
                if key not in bundle[namespace]:
                    bundle[namespace][key] = value
    
    return {
        "success": True,
        "language": language,
        "namespaces": requested_namespaces,
        "bundle": bundle,
        "generated_at": datetime.now().isoformat()
    }

@system_router.post("/i18n/detect")
async def detect_language(
    request: LanguageDetectionRequest
):
    """
    Detect language of provided text.
    
    Simple implementation based on common words.
    """
    text_lower = request.text.lower()
    
    # Simple language detection based on common words
    language_markers = {
        "es": ["el", "la", "es", "como", "por", "qué"],
        "fr": ["le", "la", "est", "comme", "pour", "quoi"],
        "de": ["der", "die", "das", "ist", "wie", "für"],
        "zh": ["的", "是", "在", "和", "了", "这"],
        "ja": ["の", "は", "です", "に", "と", "が"],
        "ar": ["ال", "في", "هو", "أن", "لم", "لماذا"],
        "pt": ["o", "a", "é", "como", "por", "que"],
        "ko": ["의", "은", "입니다", "에", "와", "무엇"]
    }
    
    scores = {}
    for lang, markers in language_markers.items():
        score = sum(1 for marker in markers if marker in text_lower)
        scores[lang] = score
    
    # Find best match
    detected = max(scores, key=scores.get) if max(scores.values()) > 0 else "en"
    
    return {
        "success": True,
        "detected_language": detected,
        "confidence": min(0.9, 0.5 + scores.get(detected, 0) * 0.1),
        "all_scores": scores,
        "text_length": len(request.text)
    }

@system_router.get("/i18n/rtl-languages")
async def get_rtl_languages():
    """
    Get list of right-to-left languages.
    """
    rtl_langs = [
        {"code": code, "name": info["name"], "native_name": info["native_name"]}
        for code, info in SUPPORTED_LANGUAGES.items()
        if info["rtl"]
    ]
    
    return {
        "success": True,
        "rtl_languages": rtl_langs,
        "count": len(rtl_langs)
    }

# =============================================================================
# API Endpoints - System Utilities
# =============================================================================

@system_router.get("/system/health/extended")
async def get_extended_health_check(
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get extended system health information.
    
    Includes version history, search index, and i18n status.
    """
    return {
        "success": True,
        "health": {
            "content_versioning": {
                "enabled": True,
                "total_content_items": len(content_history),
                "total_versions": sum(len(h.versions) for h in content_history.values())
            },
            "search": {
                "enabled": True,
                "indexed_documents": len(indexed_documents),
                "search_index_size": {
                    "courses": len(search_index.get("courses", [])),
                    "quizzes": len(search_index.get("quizzes", [])),
                    "concepts": len(search_index.get("concepts", [])),
                    "learning_paths": len(search_index.get("learning_paths", []))
                }
            },
            "internationalization": {
                "enabled": True,
                "supported_languages": len(SUPPORTED_LANGUAGES),
                "rtl_languages": len([l for l in SUPPORTED_LANGUAGES.values() if l["rtl"]]),
                "total_translation_keys": sum(
                    len(ns)
                    for translations in TRANSLATIONS.values()
                    for ns in translations.values()
                )
            }
        },
        "timestamp": datetime.now().isoformat()
    }

@system_router.get("/system/statistics")
async def get_system_statistics(
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get comprehensive system statistics.
    """
    return {
        "success": True,
        "statistics": {
            "version_control": {
                "tracked_items": len(content_history),
                "total_versions": sum(len(h.versions) for h in content_history.values()),
                "average_versions_per_item": round(
                    sum(len(h.versions) for h in content_history.values()) / len(content_history)
                    if content_history else 0, 2
                )
            },
            "search": {
                "indexed_documents": len(indexed_documents),
                "search_queries": len(search_history),
                "unique_search_terms": len(set(q.search_terms for q in search_history))
            },
            "localization": {
                "languages_supported": len(SUPPORTED_LANGUAGES),
                "translations_available": len(TRANSLATIONS),
                "namespaces": list(list(TRANSLATIONS.values())[0].keys()) if TRANSLATIONS else []
            }
        },
        "generated_at": datetime.now().isoformat()
    }

@system_router.get("/content/all/history")
async def get_all_content_history(
    content_type: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get history summary for all tracked content.
    """
    items = []
    
    for content_id, history in content_history.items():
        if content_type and history.content_type.value != content_type:
            continue
        
        latest_version = max(history.versions, key=lambda v: v.version_number)
        
        items.append({
            "content_id": content_id,
            "content_type": history.content_type.value,
            "current_version": history.current_version,
            "title": latest_version.title,
            "last_modified": latest_version.created_at.isoformat(),
            "modified_by": latest_version.created_by,
            "total_versions": len(history.versions)
        })
    
    # Sort by last modified (newest first)
    items.sort(key=lambda x: x["last_modified"], reverse=True)
    
    return {
        "success": True,
        "items": items[:limit],
        "total": len(items)
    }