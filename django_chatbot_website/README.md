# Django Chatbot Website

A Django-based web application that wraps your Chainlit chatbot in an iframe with user authentication.

## Features

- **User Authentication**: Secure login and registration system
- **Minimalist Design**: Clean, modern UI with responsive design
- **Iframe Integration**: Seamlessly embeds your Chainlit chatbot
- **Real-time Status**: Connection status monitoring for the chatbot
- **Mobile Responsive**: Works great on all device sizes

## Project Structure

```
django_chatbot_website/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── start_servers.py         # Script to start both servers
├── mysite/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── chatbot/                 # Main Django app
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   └── migrations/
├── templates/               # HTML templates
│   ├── base.html
│   ├── chatbot/
│   └── registration/
└── static/                  # CSS, JS, and static files
    ├── css/style.css
    └── js/main.js
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd django_chatbot_website
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Start Both Servers

The easiest way is to use the provided script:

```bash
python start_servers.py
```

This will start:
- Django server on http://127.0.0.1:8000
- Chainlit chatbot on http://localhost:8002

### 5. Manual Start (Alternative)

If you prefer to start servers manually:

**Terminal 1 - Start Chainlit chatbot:**
```bash
cd ../chatbot_package
python run_chatbot.py
```

**Terminal 2 - Start Django server:**
```bash
cd django_chatbot_website
python manage.py runserver
```

## Usage

1. **Access the website**: Go to http://127.0.0.1:8000
2. **Register/Login**: Create an account or login with existing credentials
3. **Chat**: Navigate to the chat page to interact with your AI data analyst
4. **Direct Chatbot Access**: You can also access the chatbot directly at http://localhost:8002

## Configuration

### Chatbot Integration

The Django app expects your Chainlit chatbot to be running on `localhost:8002`. If you need to change this:

1. Update the iframe src in `templates/chatbot/chat.html`
2. Update the connection checks in `static/js/main.js`
3. Update the `start_chatbot_server()` function in `chatbot/views.py`

### Styling

The website uses a minimalist design with:
- Inter font family
- Clean color palette (blues and grays)
- Responsive CSS Grid and Flexbox layouts
- Smooth animations and transitions

Customize the appearance by editing `static/css/style.css`.

## Features Overview

### Authentication System
- User registration with Django's built-in user model
- Secure login/logout functionality
- Protected chat interface (login required)
- Automatic redirection after login

### Chat Interface
- Full-screen iframe for seamless chatbot integration
- Connection status indicator
- Responsive design for mobile and desktop
- Error handling for connection issues

### User Experience
- Modern, minimalist design
- Loading states and transitions
- Auto-hiding notification messages
- Mobile-responsive navigation

## Troubleshooting

### Chatbot Not Loading
1. Ensure the Chainlit server is running on port 8002
2. Check if there are any port conflicts
3. Verify the chatbot_package path in `chatbot/views.py`

### Database Issues
```bash
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Port Already in Use
```bash
# For Django (port 8000)
python manage.py runserver 8001

# For Chainlit (port 8002)
# Edit the port in chatbot_package/run_chatbot.py
```

## Development

### Adding New Features
1. Create views in `chatbot/views.py`
2. Add URL patterns in `chatbot/urls.py`
3. Create templates in `templates/chatbot/`
4. Add styling in `static/css/style.css`

### Database Models
Currently using Django's built-in User model. To add custom models:
1. Edit `chatbot/models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure proper SECRET_KEY
3. Set up a proper database (PostgreSQL recommended)
4. Configure static file serving
5. Use a proper WSGI server like Gunicorn
6. Set up HTTPS and proper domain configuration

## Security Notes

- Change the SECRET_KEY in production
- Enable HTTPS in production
- Configure proper ALLOWED_HOSTS
- Consider adding rate limiting
- Use environment variables for sensitive settings
