from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
import signal
import time
import pandas as pd
import json
import numpy as np
from pathlib import Path

# Global variable to track the chatbot process
chatbot_process = None

def home(request):
    """Home page view"""
    return render(request, 'chatbot/home.html')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {username}!')
            login(request, user)
            return redirect('chat')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def chat(request):
    """Chat interface view - shows the iframe with chainlit chatbot"""
    return render(request, 'chatbot/chat.html')

@login_required
def dashboard(request):
    """Dashboard view for data analysis and visualization"""
    context = {'dataset_info': None}
    user_data_dir = Path('user_data') / str(request.user.id)
    user_data_dir.mkdir(parents=True, exist_ok=True)
    
    if request.method == 'POST' and request.FILES.get('dataset'):
        try:
            uploaded_file = request.FILES['dataset']
            
            # Validate file type
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            if file_extension not in allowed_extensions:
                messages.error(request, 'Only CSV and Excel files are supported')
                return redirect('dashboard')
            
            # Save file
            file_path = user_data_dir / uploaded_file.name
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Read the dataset
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:  # Excel files
                df = pd.read_excel(file_path)
            
            # Get dataset info
            dataset_info = {
                'filename': uploaded_file.name,
                'rows': len(df),
                'columns': len(df.columns),
                'size': f"{uploaded_file.size / 1024:.1f} KB",
                'column_names': df.columns.tolist(),
                'column_types': df.dtypes.astype(str).to_dict(),
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
                'preview_data': df.head(10).values.tolist()
            }
            
            # Store dataset info in session
            request.session['current_dataset'] = dataset_info
            context['dataset_info'] = dataset_info
            
            messages.success(request, f'Dataset {uploaded_file.name} uploaded successfully!')
            
        except Exception as e:
            messages.error(request, f'Error uploading file: {str(e)}')
            return redirect('dashboard')
    
    # Check if there's a current dataset in session
    elif 'current_dataset' in request.session:
        context['dataset_info'] = request.session['current_dataset']
    
    return render(request, 'chatbot/dashboard.html', context)

@login_required
@csrf_exempt
def upload_dataset(request):
    """Handle dataset upload"""
    if request.method == 'POST' and request.FILES.get('dataset'):
        try:
            uploaded_file = request.FILES['dataset']
            
            # Validate file type
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            if file_extension not in allowed_extensions:
                return JsonResponse({'error': 'Only CSV and Excel files are supported'}, status=400)
            
            # Create user data directory
            user_data_dir = Path('user_data') / str(request.user.id)
            user_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = user_data_dir / uploaded_file.name
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Read and analyze the dataset
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:  # Excel files
                df = pd.read_excel(file_path)
            
            # Get dataset info
            dataset_info = {
                'filename': uploaded_file.name,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'column_types': df.dtypes.astype(str).to_dict(),
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
                'missing_values': df.isnull().sum().to_dict(),
                'sample_data': df.head().to_dict('records')
            }
            
            # Store dataset info in session
            request.session['current_dataset'] = dataset_info
            
            return JsonResponse({
                'success': True,
                'message': f'Dataset {uploaded_file.name} uploaded successfully',
                'dataset_info': dataset_info
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error uploading file: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'No file uploaded'}, status=400)

@login_required
@csrf_exempt
def create_chart(request):
    """Create a chart from uploaded dataset"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chart_type = data.get('chart_type')
            x_column = data.get('x_column')
            y_column = data.get('y_column')
            
            # Get current dataset from session
            if 'current_dataset' not in request.session:
                return JsonResponse({'error': 'No dataset available'}, status=400)
            
            dataset_info = request.session['current_dataset']
            filename = dataset_info['filename']
            
            # Load the dataset
            user_data_dir = Path('user_data') / str(request.user.id)
            file_path = user_data_dir / filename
            
            if not file_path.exists():
                return JsonResponse({'error': 'Dataset file not found'}, status=404)
            
            # Read the dataset
            file_extension = Path(filename).suffix.lower()
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:  # Excel files
                df = pd.read_excel(file_path)
            
            # Generate chart data for Plotly
            chart_data = {}
            
            if chart_type == 'bar':
                if y_column:
                    # Group by x_column and sum/mean y_column
                    grouped = df.groupby(x_column)[y_column].sum()
                    chart_data = {
                        'data': [{
                            'x': grouped.index.tolist(),
                            'y': grouped.values.tolist(),
                            'type': 'bar',
                            'name': y_column
                        }],
                        'layout': {
                            'title': f'{y_column} by {x_column}',
                            'xaxis': {'title': x_column},
                            'yaxis': {'title': y_column}
                        }
                    }
                else:
                    # Count occurrences of x_column
                    value_counts = df[x_column].value_counts()
                    chart_data = {
                        'data': [{
                            'x': value_counts.index.tolist(),
                            'y': value_counts.values.tolist(),
                            'type': 'bar',
                            'name': 'Count'
                        }],
                        'layout': {
                            'title': f'Count by {x_column}',
                            'xaxis': {'title': x_column},
                            'yaxis': {'title': 'Count'}
                        }
                    }
            
            elif chart_type == 'line':
                if y_column:
                    chart_data = {
                        'data': [{
                            'x': df[x_column].tolist(),
                            'y': df[y_column].tolist(),
                            'type': 'scatter',
                            'mode': 'lines+markers',
                            'name': y_column
                        }],
                        'layout': {
                            'title': f'{y_column} vs {x_column}',
                            'xaxis': {'title': x_column},
                            'yaxis': {'title': y_column}
                        }
                    }
            
            elif chart_type == 'pie':
                value_counts = df[x_column].value_counts()
                chart_data = {
                    'data': [{
                        'values': value_counts.values.tolist(),
                        'labels': value_counts.index.tolist(),
                        'type': 'pie'
                    }],
                    'layout': {
                        'title': f'Distribution of {x_column}'
                    }
                }
            
            elif chart_type == 'scatter':
                if y_column:
                    chart_data = {
                        'data': [{
                            'x': df[x_column].tolist(),
                            'y': df[y_column].tolist(),
                            'mode': 'markers',
                            'type': 'scatter',
                            'name': f'{y_column} vs {x_column}'
                        }],
                        'layout': {
                            'title': f'{y_column} vs {x_column}',
                            'xaxis': {'title': x_column},
                            'yaxis': {'title': y_column}
                        }
                    }
            
            elif chart_type == 'histogram':
                chart_data = {
                    'data': [{
                        'x': df[x_column].tolist(),
                        'type': 'histogram',
                        'name': x_column
                    }],
                    'layout': {
                        'title': f'Distribution of {x_column}',
                        'xaxis': {'title': x_column},
                        'yaxis': {'title': 'Frequency'}
                    }
                }
            
            return JsonResponse({
                'success': True,
                'chart_json': json.dumps(chart_data)
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error creating chart: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
@csrf_exempt
def get_dataset_info(request):
    """Get information about a specific dataset"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filename = data.get('filename')
            
            user_data_dir = Path('user_data') / str(request.user.id)
            file_path = user_data_dir / filename
            
            if not file_path.exists():
                return JsonResponse({'error': 'Dataset not found'}, status=404)
            
            # Read the dataset based on file extension
            file_extension = Path(filename).suffix.lower()
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:  # Excel files
                df = pd.read_excel(file_path)
            
            dataset_info = {
                'filename': filename,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'column_types': df.dtypes.astype(str).to_dict(),
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
                'missing_values': df.isnull().sum().to_dict(),
                'sample_data': df.head(10).to_dict('records'),
                'summary_stats': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
            }
            
            return JsonResponse({
                'success': True,
                'dataset_info': dataset_info
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error loading dataset: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def start_chatbot_server():
    """Start the Chainlit chatbot server if not already running"""
    global chatbot_process
    
    if chatbot_process and chatbot_process.poll() is None:
        return True  # Already running
    
    try:
        # Path to your chatbot package
        chatbot_root = Path(__file__).parent.parent.parent / "chatbot_package"
        run_script = chatbot_root / "run_chatbot.py"
        
        if not run_script.exists():
            print(f"Chatbot script not found at {run_script}")
            return False
        
        # Start the chatbot server on port 8002
        chatbot_process = subprocess.Popen(
            ["python", str(run_script)],
            cwd=str(chatbot_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        return chatbot_process.poll() is None
        
    except Exception as e:
        print(f"Error starting chatbot: {e}")
        return False

def stop_chatbot_server():
    """Stop the Chainlit chatbot server"""
    global chatbot_process
    
    if chatbot_process and chatbot_process.poll() is None:
        try:
            chatbot_process.terminate()
            chatbot_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            chatbot_process.kill()
        chatbot_process = None
