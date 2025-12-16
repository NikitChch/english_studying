@echo off
dir /s /b | findstr /v /i "__pycache__ migrations .pyc .pyo .sqlite3" > project_structure.txt