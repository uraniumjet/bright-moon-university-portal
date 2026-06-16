"""
The Bright Moon University - Security & Authentication Ledger
File: models/auth.py
Description: Manages login credentials, permission scopes, and account states.
"""

from typing import Optional
from sqlmodel import SQLModel, Field

class UserAccount(SQLModel, table=True):
    """
    Central authentication repository. Stores access tokens, hashed passwords, 
    and handles account status states for all actors.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True) # Unique Institutional ID (e.g., UR-2026-0001)
    hashed_password: str
    role: str = Field(index=True) # "onboarder", "student", "faculty", "exam_office", "admin"
    is_active: bool = Field(default=True)
    
    # Onboarding workflow: forces user to change password or choose to maintain it on first entry
    requires_password_reset: bool = Field(default=True)