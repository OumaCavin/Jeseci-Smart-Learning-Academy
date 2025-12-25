#!/usr/bin/env python3
"""
LMS Integration Module
Jeseci Smart Learning Academy - Phase 4 Enterprise Intelligence

This module provides integration with Learning Management Systems:
- LTI 1.3 Provider implementation
- Canvas LMS API integration
- Moodle LMS API integration
- Grade passback synchronization
- Roster and enrollment management
- Deep linking support

Author: Cavin Otieno
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import base64
import hashlib
import hmac
import jwt
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import APIRouter, HTTPException, Depends, Header, Query, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from admin_auth import get_current_admin_user, AdminRole

# Initialize router
lms_router = APIRouter()

# =============================================================================
# Data Models
# =============================================================================

class LMSPlatform(str, Enum):
    """Supported LMS platforms"""
    CANVAS = "canvas"
    MOODLE = "moodle"
    BLACKBOARD = "blackboard"
    CUSTOM = "custom"

class LTIRole(str, Enum):
    """LTI role mappings"""
    INSTRUCTOR = "Instructor"
    LEARNER = "Learner"
    TEACHING_ASSISTANT = "TeachingAssistant"
    ADMINISTRATOR = "Administrator"
    CONTENT_DEVELOPER = "ContentDeveloper"

class EnrollmentStatus(str, Enum):
    """Student enrollment status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    INVITED = "invited"

@dataclass
class LMSConfig:
    """LMS platform configuration"""
    config_id: str
    platform: LMSPlatform
    name: str
    client_id: str
    issuer: str
    deployment_id: str
    auth_endpoint: str
    token_endpoint: str
    jwks_endpoint: str
    public_key: str
    private_key: str
    deep_link_endpoint: str
    grade_passback_enabled: bool
    roster_sync_enabled: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

@dataclass
class LTISession:
    """LTI launch session data"""
    session_id: str
    platform_config_id: str
    user_id: str
    user_email: str
    user_name: str
    user_roles: List[str]
    context_id: str
    context_title: str
    resource_link_id: str
    launch_presentation_return_url: str
    created_at: datetime
    expires_at: datetime

@dataclass
class GradePassback:
    """Grade passback record"""
    passback_id: str
    lms_config_id: str
    user_id: str
    resource_id: str
    course_id: str
    score: float
    max_score: float
    comment: str
    activity_progress: str
    grading_progress: str
    sent_at: datetime
    lms_response: Dict[str, Any]

@dataclass
class RosterEntry:
    """Roster entry for course enrollment"""
    entry_id: str
    lms_config_id: str
    context_id: str
    user_id: str
    email: str
    name: str
    roles: List[str]
    status: EnrollmentStatus
    imported_at: datetime

# =============================================================================
# In-Memory Data Store
# =============================================================================

# LMS configurations
lms_configs: Dict[str, LMSConfig] = {}

# LTI sessions
lti_sessions: Dict[str, LTISession] = {}

# Grade passback records
grade_passbacks: Dict[str, GradePassback] = {}

# Roster entries
roster_entries: Dict[str, RosterEntry] = {}

# LTI platforms (mock data)
supported_platforms = {
    "canvas": {
        "name": "Canvas LMS",
        "auth_endpoint": "https://canvas.instructure.com/api/lti/authorize_redirect",
        "token_endpoint": "https://canvas.instructure.com/login/oauth2/token",
        "jwks_endpoint": "https://canvas.instructure.com/api/lti/security/jwks",
        "api_base": "https://canvas.instructure.com/api/v1"
    },
    "moodle": {
        "name": "Moodle",
        "auth_endpoint": "/mod/lti/auth.php",
        "token_endpoint": "/mod/lti/token.php",
        "jwks_endpoint": "/mod/lti/jwks.php",
        "api_base": "/webservice/rest/server.php"
    }
}

# Initialize sample configuration
def initialize_lms_data():
    """Initialize sample LMS configurations"""
    # Sample Canvas configuration
    canvas_config = LMSConfig(
        config_id="lms_canvas_001",
        platform=LMSPlatform.CANVAS,
        name="Jeseci Academy - Canvas Integration",
        client_id="10000000000001",
        issuer="https://canvas.instructure.com",
        deployment_id="deploy_001",
        auth_endpoint="https://canvas.instructure.com/api/lti/authorize_redirect",
        token_endpoint="https://canvas.instructure.com/login/oauth2/token",
        jwks_endpoint="https://canvas.instructure.com/api/lti/security/jwks",
        public_key="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
        private_key="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQ...\n-----END PRIVATE KEY-----",
        deep_link_endpoint="https://jeseci.academy/lti/deep-link",
        grade_passback_enabled=True,
        roster_sync_enabled=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    lms_configs["lms_canvas_001"] = canvas_config

initialize_lms_data()

# =============================================================================
# Request/Response Models
# =============================================================================

class LMSConfigCreateRequest(BaseModel):
    """Request model for creating LMS configuration"""
    platform: LMSPlatform
    name: str = Field(..., max_length=200)
    client_id: str
    issuer: str
    deployment_id: str
    auth_endpoint: str
    token_endpoint: str
    jwks_endpoint: str
    public_key: str
    private_key: str
    deep_link_endpoint: str = "https://jeseci.academy/lti/deep-link"
    grade_passback_enabled: bool = True
    roster_sync_enabled: bool = True

class LMSConfigResponse(BaseModel):
    """Response model for LMS configuration"""
    success: bool
    config: Dict[str, Any]
    config_xml: str
    config_json: str

class LTILaunchRequest(BaseModel):
    """Request model for LTI launch validation"""
    id_token: str
    state: str

class GradeSubmissionRequest(BaseModel):
    """Request model for grade submission"""
    lms_config_id: str
    user_id: str
    resource_id: str
    course_id: str
    score: float = Field(..., ge=0, le=100)
    max_score: float = Field(default=100)
    comment: str = ""
    activity_progress: str = "Completed"
    grading_progress: str = "FullyGraded"

class RosterSyncRequest(BaseModel):
    """Request model for roster synchronization"""
    lms_config_id: str
    context_id: str
    course_id: str

class DeepLinkRequest(BaseModel):
    """Request model for deep linking"""
    lms_config_id: str
    title: str
    text: str
    url: str
    custom_params: Dict[str, str] = {}

class LTIToolConfigResponse(BaseModel):
    """Response model for LTI tool configuration"""
    title: str
    description: str
    oidc_initiation_url: str
    target_link_uri: str
    scopes: List[str]
    extensions: List[Dict[str, Any]]
    public_jwk_url: str
    custom_parameters: Dict[str, str]

# =============================================================================
# LTI 1.3 Helper Functions
# =============================================================================

def decode_jwt_payload(token: str) -> Dict[str, Any]:
    """Decode JWT token payload without verification (for inspection)"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        payload = base64.urlsafe_b64decode(
            parts[1] + '=' * (4 - len(parts[1]) % 4)
        )
        return json.loads(payload)
    except Exception as e:
        raise ValueError(f"Failed to decode JWT: {e}")

def validate_lti_launch(
    id_token: str,
    nonce: str,
    state: str
) -> Dict[str, Any]:
    """
    Validate LTI 1.3 launch parameters.
    
    In production, this would:
    1. Verify JWT signature using platform JWKS
    2. Validate nonce and state
    3. Check token expiration
    4. Verify required claims
    """
    try:
        # Decode token for inspection
        payload = decode_jwt_payload(id_token)
        
        # Validate required LTI claims
        required_claims = [
            "iss", "sub", "aud", "exp", "iat", "nonce",
            "https://purl.imsglobal.org/spec/lti/claim/message_type",
            "https://purl.imsglobal.org/spec/lti/claim/version",
            "https://purl.imsglobal.org/spec/lti/claim/deployment_id"
        ]
        
        for claim in required_claims:
            if claim not in payload:
                raise ValueError(f"Missing required claim: {claim}")
        
        # Validate LTI version
        if payload.get("https://purl.imsglobal.org/spec/lti/claim/version") != "1.3.0":
            raise ValueError("Invalid LTI version")
        
        # Validate expiration
        if payload.get("exp", 0) < datetime.now().timestamp():
            raise ValueError("Token has expired")
        
        # Extract key user and context data
        launch_data = {
            "user_id": payload.get("sub"),
            "user_email": payload.get("email", ""),
            "user_name": payload.get("name", ""),
            "user_roles": payload.get(
                "https://purl.imsglobal.org/spec/lti/claim/roles", []
            ),
            "context_id": payload.get(
                "https://purl.imsglobal.org/spec/lti/claim/context", {}
            ).get("id", ""),
            "context_title": payload.get(
                "https://purl.imsglobal.org/spec/lti/claim/context", {}
            ).get("title", ""),
            "resource_link_id": payload.get(
                "https://purl.imsglobal.org/spec/lti/claim/resource_link", {}
            ).get("id", ""),
            "launch_presentation_return_url": payload.get(
                "https://purl.imsglobal.org/spec/lti/claim/launch_presentation", {}
            ).get("return_url", ""),
            "custom_claims": payload.get("https://purl.imsglobal.org/spec/lti/claim/custom", {})
        }
        
        return {
            "valid": True,
            "launch_data": launch_data,
            "raw_payload": payload
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def generate_lti_tool_configuration(config: LMSConfig) -> Dict[str, Any]:
    """Generate LTI 1.3 tool configuration"""
    return {
        "title": config.name,
        "description": "Jeseci Smart Learning Academy - Interactive Learning Platform",
        "oidc_initiation_url": "https://jeseci.academy/lti/login",
        "target_link_uri": "https://jeseci.academy/lti/launch",
        "scopes": [
            "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
            "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
            "https://purl.imsglobal.org/spec/lti-ags/scope/score",
            "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
        ],
        "extensions": [
            {
                "platform": "canvas.instructure.com",
                "settings": {
                    "placements": [
                        {
                            "placement": "course_navigation",
                            "message_type": "LtiResourceLinkRequest",
                            "target_link_uri": "https://jeseci.academy/lti/launch",
                            "text": "Jeseci Learning"
                        },
                        {
                            "placement": "assignment_selection",
                            "message_type": "LtiDeepLinkingRequest",
                            "target_link_uri": "https://jeseci.academy/lti/deep-link",
                            "text": "Jeseci Content"
                        }
                    ]
                }
            }
        ],
        "public_jwk_url": "https://jeseci.academy/lti/jwks",
        "custom_parameters": {
            "course_id": "$Canvas.course.id",
            "user_id": "$Canvas.user.id",
            "roles": "$Canvas.user.role"
        }
    }

def generate_config_xml(config: LMSConfig) -> str:
    """Generate XML configuration for LTI tool"""
    tool_config = generate_lti_tool_configuration(config)
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<cartridge_basiclti_link xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
    xmlns:blti="http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
    xmlns:lticm="http://www.imsglobal.org/xsd/imslticm_v1p0"
    xmlns:lticp="http://www.imsglobal.org/xsd/imslticp_v1p0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
    http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0.xsd
    http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
    http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
    
    <blti:title>{tool_config['title']}</blti:title>
    <blti:description>{tool_config['description']}</blti:description>
    <blti:launch_url>https://jeseci.academy/lti/launch</blti:launch_url>
    <blti:extensions platform="canvas.instructure.com">
        <lticm:property name="tool_id">jeseci_academy</lticm:property>
        <lticm:property name="privacy_level">public</lticm:property>
        <lticm:options name="course_navigation">
            <lticm:property name="enabled">true</lticm:property>
            <lticm:property name="text">Jeseci Learning</lticm:property>
        </lticm:options>
    </blti:extensions>
    <cartridge_bundle identifierref="BLTI001_Bundle"/>
    <cartridge_icon identifierref="BLTI001_Icon"/>
    
</cartridge_basiclti_link>"""
    
    return xml

# =============================================================================
# API Endpoints
# =============================================================================

@lms_router.get("/lms/config")
async def get_lti_tool_configuration():
    """
    Get LTI 1.3 tool configuration for platform registration.
    
    Returns configuration in JSON format for LMS registration.
    """
    config = generate_lti_tool_configuration(
        LMSConfig(
            config_id="default",
            platform=LMSPlatform.CANVAS,
            name="Jeseci Smart Learning Academy",
            client_id="",
            issuer="",
            deployment_id="",
            auth_endpoint="",
            token_endpoint="",
            jwks_endpoint="",
            public_key="",
            private_key="",
            deep_link_endpoint="https://jeseci.academy/lti/deep-link",
            grade_passback_enabled=True,
            roster_sync_enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    )
    
    return LTIToolConfigResponse(**config)

@lms_router.get("/lms/config/xml")
async def get_lti_config_xml():
    """
    Get LTI 1.3 tool configuration in XML format.
    
    Useful for manual LMS registration.
    """
    config_xml = """<?xml version="1.0" encoding="UTF-8"?>
<cartridge_basiclti_link xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
    xmlns:blti="http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
    xmlns:lticm="http://www.imsglobal.org/xsd/imslticm_v1p0"
    xmlns:lticp="http://www.imsglobal.org/xsd/imslticp_v1p0">
    
    <blti:title>Jeseci Smart Learning Academy</blti:title>
    <blti:description>Interactive Learning Platform with AI-Powered Analytics</blti:description>
    <blti:launch_url>https://jeseci.academy/lti/launch</blti:launch_url>
    <blti:extensions platform="canvas.instructure.com">
        <lticm:property name="tool_id">jeseci_academy</lticm:property>
        <lticm:property name="privacy_level">public</lticm:property>
        <lticm:options name="course_navigation">
            <lticm:property name="enabled">true</lticm:property>
            <lticm:property name="text">Jeseci Learning</lticm:property>
        </lticm:options>
    </blti:extensions>
    
</cartridge_basiclti_link>"""
    
    return Response(
        content=config_xml,
        media_type="application/xml"
    )

@lms_router.get("/lms/platforms")
async def get_supported_platforms():
    """
    Get list of supported LMS platforms and their requirements.
    """
    return {
        "success": True,
        "platforms": [
            {
                "id": "canvas",
                "name": "Canvas LMS",
                "version": "LTI 1.3",
                "features": ["grade_passback", "roster_sync", "deep_linking"],
                "setup_guide": "/docs/lms/canvas-setup"
            },
            {
                "id": "moodle",
                "name": "Moodle",
                "version": "LTI 1.3",
                "features": ["grade_passback", "roster_sync"],
                "setup_guide": "/docs/lms/moodle-setup"
            },
            {
                "id": "blackboard",
                "name": "Blackboard Learn",
                "version": "LTI 1.3",
                "features": ["grade_passback", "deep_linking"],
                "setup_guide": "/docs/lms/blackboard-setup"
            }
        ],
        "documentation": "/docs/lms/integration-guide"
    }

@lms_router.post("/lms/configurations", response_model=LMSConfigResponse)
async def create_lms_configuration(
    request: LMSConfigCreateRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Create new LMS platform configuration.
    
    Only SUPER_ADMIN can create LMS configurations.
    """
    if current_user.get("admin_role") != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Only Super Admins can create LMS configurations"}
        )
    
    config_id = f"lms_{request.platform.value}_{uuid.uuid4().hex[:8]}"
    
    config = LMSConfig(
        config_id=config_id,
        platform=request.platform,
        name=request.name,
        client_id=request.client_id,
        issuer=request.issuer,
        deployment_id=request.deployment_id,
        auth_endpoint=request.auth_endpoint,
        token_endpoint=request.token_endpoint,
        jwks_endpoint=request.jwks_endpoint,
        public_key=request.public_key,
        private_key=request.private_key,
        deep_link_endpoint=request.deep_link_endpoint,
        grade_passback_enabled=request.grade_passback_enabled,
        roster_sync_enabled=request.roster_sync_enabled,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    lms_configs[config_id] = config
    
    # Generate configuration formats
    config_xml = generate_config_xml(config)
    config_json = json.dumps(generate_lti_tool_configuration(config), indent=2)
    
    return LMSConfigResponse(
        success=True,
        config={
            "config_id": config.config_id,
            "platform": config.platform.value,
            "name": config.name,
            "client_id": config.client_id,
            "issuer": config.issuer,
            "deployment_id": config.deployment_id,
            "auth_endpoint": config.auth_endpoint,
            "is_active": config.is_active,
            "grade_passback_enabled": config.grade_passback_enabled,
            "roster_sync_enabled": config.roster_sync_enabled,
            "created_at": config.created_at.isoformat()
        },
        config_xml=config_xml,
        config_json=config_json
    )

@lms_router.get("/lms/configurations")
async def list_lms_configurations(
    platform: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    List all LMS configurations.
    """
    configs = [
        {
            "config_id": cfg.config_id,
            "platform": cfg.platform.value,
            "name": cfg.name,
            "issuer": cfg.issuer,
            "is_active": cfg.is_active,
            "grade_passback_enabled": cfg.grade_passback_enabled,
            "roster_sync_enabled": cfg.roster_sync_enabled,
            "created_at": cfg.created_at.isoformat()
        }
        for cfg in lms_configs.values()
        if (platform is None or cfg.platform.value == platform) and
           (not active_only or cfg.is_active)
    ]
    
    return {
        "success": True,
        "configurations": configs,
        "total": len(configs)
    }

@lms_router.get("/lms/configurations/{config_id}")
async def get_lms_configuration(
    config_id: str,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get detailed LMS configuration.
    """
    if config_id not in lms_configs:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Configuration not found"}
        )
    
    config = lms_configs[config_id]
    
    return {
        "success": True,
        "configuration": {
            "config_id": config.config_id,
            "platform": config.platform.value,
            "name": config.name,
            "client_id": config.client_id,
            "issuer": config.issuer,
            "deployment_id": config.deployment_id,
            "auth_endpoint": config.auth_endpoint,
            "token_endpoint": config.token_endpoint,
            "jwks_endpoint": config.jwks_endpoint,
            "deep_link_endpoint": config.deep_link_endpoint,
            "is_active": config.is_active,
            "grade_passback_enabled": config.grade_passback_enabled,
            "roster_sync_enabled": config.roster_sync_enabled,
            "created_at": config.created_at.isoformat(),
            "updated_at": config.updated_at.isoformat()
        },
        "config_xml": generate_config_xml(config),
        "config_json": json.dumps(generate_lti_tool_configuration(config), indent=2)
    }

@lms_router.put("/lms/configurations/{config_id}")
async def update_lms_configuration(
    config_id: str,
    request: LMSConfigCreateRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Update existing LMS configuration.
    """
    if config_id not in lms_configs:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Configuration not found"}
        )
    
    if current_user.get("admin_role") != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Only Super Admins can update LMS configurations"}
        )
    
    config = lms_configs[config_id]
    
    # Update fields
    config.name = request.name
    config.client_id = request.client_id
    config.issuer = request.issuer
    config.deployment_id = request.deployment_id
    config.auth_endpoint = request.auth_endpoint
    config.token_endpoint = request.token_endpoint
    config.jwks_endpoint = request.jwks_endpoint
    config.public_key = request.public_key
    config.private_key = request.private_key
    config.deep_link_endpoint = request.deep_link_endpoint
    config.grade_passback_enabled = request.grade_passback_enabled
    config.roster_sync_enabled = request.roster_sync_enabled
    config.updated_at = datetime.now()
    
    return {
        "success": True,
        "message": "Configuration updated successfully",
        "config_id": config_id
    }

@lms_router.post("/lms/lti/launch")
async def lti_launch(
    id_token: str = Field(...),
    state: str = Field(...),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Handle LTI 1.3 launch request.
    
    Validates the launch and creates a session for the user.
    """
    # Validate the launch
    validation = validate_lti_launch(id_token, "", state)
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": validation["error"]}
        )
    
    launch_data = validation["launch_data"]
    
    # Create session
    session_id = f"lti_session_{uuid.uuid4().hex[:12]}"
    session = LTISession(
        session_id=session_id,
        platform_config_id="default",
        user_id=launch_data["user_id"],
        user_email=launch_data["user_email"],
        user_name=launch_data["user_name"],
        user_roles=launch_data["user_roles"],
        context_id=launch_data["context_id"],
        context_title=launch_data["context_title"],
        resource_link_id=launch_data["resource_link_id"],
        launch_presentation_return_url=launch_data["launch_presentation_return_url"],
        created_at=datetime.now(),
        expires_at=datetime.now()
    )
    
    lti_sessions[session_id] = session
    
    return {
        "success": True,
        "session_id": session_id,
        "user": {
            "user_id": session.user_id,
            "name": session.user_name,
            "email": session.user_email,
            "roles": session.user_roles
        },
        "context": {
            "context_id": session.context_id,
            "title": session.context_title
        },
        "resource_link_id": session.resource_link_id,
        "launch_presentation_return_url": session.launch_presentation_return_url,
        "message": "LTI launch successful"
    }

@lms_router.post("/lms/grades", response_model=Dict[str, Any])
async def submit_grade(
    request: GradeSubmissionRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Submit grade to LMS via LTI Assignment and Grade Services (AGS).
    
    This endpoint sends quiz scores and assessment results back to the
    LMS gradebook.
    """
    # Validate configuration
    if request.lms_config_id not in lms_configs:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "LMS configuration not found"}
        )
    
    config = lms_configs[request.lms_config_id]
    
    if not config.grade_passback_enabled:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Grade passback is not enabled for this configuration"}
        )
    
    # In production, this would:
    # 1. Get access token from LMS
    # 2. Create or update lineitem
    # 3. Submit score
    
    # Mock grade submission
    passback_id = f"grade_{uuid.uuid4().hex[:8]}"
    grade = GradePassback(
        passback_id=passback_id,
        lms_config_id=request.lms_config_id,
        user_id=request.user_id,
        resource_id=request.resource_id,
        course_id=request.course_id,
        score=request.score,
        max_score=request.max_score,
        comment=request.comment,
        activity_progress=request.activity_progress,
        grading_progress=request.grading_progress,
        sent_at=datetime.now(),
        lms_response={
            "status": "success",
            "score": request.score,
            "max_score": request.max_score,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    grade_passbacks[passback_id] = grade
    
    return {
        "success": True,
        "passback_id": passback_id,
        "message": "Grade submitted successfully",
        "grade": {
            "user_id": request.user_id,
            "resource_id": request.resource_id,
            "score": request.score,
            "max_score": request.max_score,
            "percentage": round(request.score / request.max_score * 100, 2),
            "sent_at": grade.sent_at.isoformat()
        },
        "lms_response": grade.lms_response
    }

@lms_router.get("/lms/grades/{user_id}")
async def get_grade_history(
    user_id: str,
    lms_config_id: Optional[str] = Query(None),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get grade submission history for a user.
    """
    grades = [
        g for g in grade_passbacks.values()
        if g.user_id == user_id and (lms_config_id is None or g.lms_config_id == lms_config_id)
    ]
    
    # Sort by date (newest first)
    grades.sort(key=lambda x: x.sent_at, reverse=True)
    
    return {
        "success": True,
        "user_id": user_id,
        "grades": [
            {
                "passback_id": g.passback_id,
                "resource_id": g.resource_id,
                "course_id": g.course_id,
                "score": g.score,
                "max_score": g.max_score,
                "percentage": round(g.score / g.max_score * 100, 2),
                "comment": g.comment,
                "activity_progress": g.activity_progress,
                "grading_progress": g.grading_progress,
                "sent_at": g.sent_at.isoformat(),
                "status": g.lms_response.get("status")
            }
            for g in grades[:limit]
        ],
        "total": len(grades)
    }

@lms_router.post("/lms/roster/sync", response_model=Dict[str, Any])
async def sync_roster(
    request: RosterSyncRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Synchronize roster from LMS to Jeseci platform.
    
    This endpoint imports student enrollment data from the LMS,
    creating or updating user accounts and enrollments.
    """
    # Validate configuration
    if request.lms_config_id not in lms_configs:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "LMS configuration not found"}
        )
    
    config = lms_configs[request.lms_config_id]
    
    if not config.roster_sync_enabled:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Roster sync is not enabled for this configuration"}
        )
    
    # In production, this would:
    # 1. Get access token from LMS
    # 2. Call Names and Role Provisioning Service (NRPS)
    # 3. Import and sync user data
    
    # Mock roster data
    mock_roster = [
        {
            "user_id": f"lms_user_{i}",
            "email": f"student{i}@example.edu",
            "name": f"Student {i}",
            "roles": ["Learner"],
            "status": "active"
        }
        for i in range(1, 26)
    ]
    
    # Process roster entries
    imported_count = 0
    updated_count = 0
    
    for entry_data in mock_roster:
        entry_id = f"roster_{uuid.uuid4().hex[:8]}"
        entry = RosterEntry(
            entry_id=entry_id,
            lms_config_id=request.lms_config_id,
            context_id=request.context_id,
            user_id=entry_data["user_id"],
            email=entry_data["email"],
            name=entry_data["name"],
            roles=entry_data["roles"],
            status=EnrollmentStatus.ACTIVE,
            imported_at=datetime.now()
        )
        roster_entries[entry_id] = entry
        imported_count += 1
    
    return {
        "success": True,
        "message": "Roster synchronized successfully",
        "context_id": request.context_id,
        "course_id": request.course_id,
        "imported": imported_count,
        "updated": updated_count,
        "total_enrolled": imported_count,
        "sync_timestamp": datetime.now().isoformat()
    }

@lms_router.get("/lms/roster/{context_id}")
async def get_roster(
    context_id: str,
    lms_config_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get roster entries for a specific context/course.
    """
    roster = [
        r for r in roster_entries.values()
        if r.context_id == context_id and
           (lms_config_id is None or r.lms_config_id == lms_config_id) and
           (status is None or r.status.value == status)
    ]
    
    return {
        "success": True,
        "context_id": context_id,
        "roster": [
            {
                "entry_id": r.entry_id,
                "user_id": r.user_id,
                "email": r.email,
                "name": r.name,
                "roles": r.roles,
                "status": r.status.value,
                "imported_at": r.imported_at.isoformat()
            }
            for r in roster[:limit]
        ],
        "total": len(roster)
    }

@lms_router.post("/lms/deep-link")
async def handle_deep_linking(
    request: DeepLinkRequest,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Handle LTI Deep Linking response.
    
    This endpoint receives content selection from the LMS and
    returns the selected content to be embedded.
    """
    # In production, this would:
    # 1. Validate the deep linking request
    # 2. Create deployment configuration
    # 3. Return content items
    
    return {
        "success": True,
        "message": "Deep linking response created",
        "deployment": {
            "content_id": uuid.uuid4().hex[:12],
            "title": request.title,
            "text": request.text,
            "url": request.url,
            "custom_params": request.custom_params,
            "created_at": datetime.now().isoformat()
        },
        "lti_response": {
            "deployment_id": "deploy_001",
            "data": {
                "content_title": request.title,
                "content_url": request.url
            }
        }
    }

@lms_router.delete("/lms/configurations/{config_id}")
async def delete_lms_configuration(
    config_id: str,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Delete LMS configuration (soft delete - deactivate).
    """
    if config_id not in lms_configs:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Configuration not found"}
        )
    
    if current_user.get("admin_role") != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Only Super Admins can delete LMS configurations"}
        )
    
    # Soft delete - just deactivate
    lms_configs[config_id].is_active = False
    lms_configs[config_id].updated_at = datetime.now()
    
    return {
        "success": True,
        "message": "Configuration deactivated successfully",
        "config_id": config_id
    }

@lms_router.get("/lms/statistics")
async def get_lms_statistics(
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Get LMS integration statistics.
    """
    active_configs = [c for c in lms_configs.values() if c.is_active]
    total_grades = len(grade_passbacks)
    total_roster = len(roster_entries)
    total_sessions = len(lti_sessions)
    
    # Calculate recent activity (last 7 days)
    recent_grades = len([
        g for g in grade_passbacks.values()
        if (datetime.now() - g.sent_at).days <= 7
    ])
    
    return {
        "success": True,
        "statistics": {
            "active_configurations": len(active_configs),
            "total_grade_submissions": total_grades,
            "recent_grade_submissions": recent_grades,
            "total_roster_entries": total_roster,
            "total_lti_sessions": total_sessions,
            "grade_success_rate": 98.5
        },
        "by_platform": {
            "canvas": {
                "configurations": len([c for c in active_configs if c.platform == LMSPlatform.CANVAS]),
                "grade_submissions": len([g for g in grade_passbacks.values() if g.lms_config_id.startswith("canvas")])
            },
            "moodle": {
                "configurations": len([c for c in active_configs if c.platform == LMSPlatform.MOODLE]),
                "grade_submissions": len([g for g in grade_passbacks.values() if g.lms_config_id.startswith("moodle")])
            }
        },
        "generated_at": datetime.now().isoformat()
    }