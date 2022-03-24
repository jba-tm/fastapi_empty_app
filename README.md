# fastapi_empty_app

This app can be deployed with docker-compose. For build containers simple run this script on the shell:
    
    ./scripts/build.sh


Project env vars: 
    
    BACKEND_HOST - "0.0.0.0" backend host 
    BACKEND_PORT - "8080" backend port
    FIRST_SUPERUSER - "admin@example.com" user email on project
    FIRST_SUPERUSER_PASSWORD - "change_this" user password on project
    SMTP_USER - "no-reply@example.com" smtp send email
    SMTP_PASSWORD - "change_this" smtp email password
    EMAILS_FROM_EMAIL - "info@example.com" smtp send email
    