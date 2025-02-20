# Delta_Project
# Delta V2


Delta V2 is a Django project using Office365 login with Django Allauth. It connects to a PostgreSQL database and follows good practices by using an `.env` file for config.

## How to Set Up

```bash
# 1. Clone the Project
git clone https://github.com/Cann-E/Delta-V2.git
cd Delta-V2

# 2. Set Up a Virtual Environment
python -m venv venv
source venv/Scripts/activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# 3. Install What You Need
pip install -r requirements.txt

# 4. Add a `.env` File ALREADY INCLUDED
echo "SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_NAME=delta_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_SECRET=your-client-secret" > .env

# 5. Migrate the Database
python manage.py makemigrations
python manage.py migrate

# 6. Run the Server
python manage.py runserver

Group Name:Delta
