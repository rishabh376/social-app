#!/bin/bash
set -e

echo "🚀 Social App Setup"
echo "=================="

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements/base.txt

# Create .env file if not exists
if [ ! -f .env ]; then
    cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DB_NAME=socialdb
DB_USER=socialuser
DB_PASSWORD=socialpass
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
    echo "✅ Created .env file"
fi

# Run migrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static
python manage.py collectstatic --noinput

echo "✅ Setup complete! Run: python manage.py runserver"
