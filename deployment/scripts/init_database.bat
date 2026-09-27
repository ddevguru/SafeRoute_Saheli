@echo off
echo ========================================================
echo   SafeRoute Saheli - Database Initialization Utility
echo ========================================================

set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASS=rootpassword
set DB_NAME=saferoute_saheli

echo Importing schema.sql...
mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASS% %DB_NAME% < ..\..\database\schema.sql
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to import schema.sql. Please ensure MySQL is running.
    exit /b 1
)

echo Importing seed_data.sql...
mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASS% %DB_NAME% < ..\..\database\seed_data.sql
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to import seed_data.sql.
    exit /b 1
)

echo [SUCCESS] SafeRoute Saheli database initialized with benchmark tables and seed data!
exit /b 0
