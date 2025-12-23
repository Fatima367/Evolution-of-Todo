---
id: 0012
title: fix-bcrypt-password-length-limitation
stage: red
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: backend-auth
branch: 002-todo-web
user: user
command: "Fix bcrypt password length issue"
labels: ["auth", "security", "bcrypt", "validation", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase2-todo-web/backend/src/auth/security.py
  - phase2-todo-web/backend/src/schemas/user_schemas.py
tests: []
---

# Fix bcrypt password length limitation

## Problem
The application was experiencing a `ValueError: password cannot be longer than 72 bytes, truncate manually if necessary` error during user registration when users entered passwords longer than 72 bytes.

## Root Cause
Bcrypt has a hard limitation of 72 bytes for password length. When passwords exceed this limit, bcrypt throws an error during the hashing process.

## Changes Made

### 1. Enhanced Password Validation in Schema
Updated `src/schemas/user_schemas.py` to validate password length at the schema level:
- Added field validator to check if password exceeds 72 bytes when UTF-8 encoded
- Returns clear error message to users about the limitation

### 2. Improved Password Hashing Function
Updated `src/auth/security.py` with robust truncation logic:
- Enhanced `hash_password()` function with proper byte-length validation
- Added handling for multi-byte characters to avoid cutting them in the middle
- Updated `verify_password()` function with consistent truncation logic

## Testing Results
- Long ASCII passwords (80+ characters) are rejected at schema validation
- Multi-byte character passwords (>72 bytes when encoded) are handled properly
- Normal passwords (<72 bytes) work as expected
- Password verification works consistently with truncated passwords

## Impact
- User registration now properly validates password length before bcrypt hashing
- Clear error messages inform users about password length requirements
- No more internal server errors due to bcrypt limitations
- Maintains security while handling the bcrypt constraint gracefully