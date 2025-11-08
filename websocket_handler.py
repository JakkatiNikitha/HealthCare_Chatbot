from flask_socketio import SocketIO, emit, join_room
from flask import session
import logging
from datetime import datetime
import time

# Initialize SocketIO with Flask app
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('websocket')

@socketio.on('connect')
def handle_connect():
    """Handle authenticated client connection"""
    if 'user_id' not in session:
        logger.warning('Unauthorized connection attempt')
        return False
    
    user_id = session['user_id']
    join_room(user_id)
    logger.info(f'Client connected: {user_id}')
    emit('connection_response', {
        'status': 'connected',
        'timestamp': datetime.now().isoformat()
    }, room=user_id)

@socketio.on('disconnect')
def handle_disconnect(sid):
    """Handle client disconnection with reconnection support"""
    user_id = session.get('user_id')
    if user_id:
        logger.info(f'Client disconnected: {user_id}')
        emit('connection_response', {
            'status': 'disconnected',
            'timestamp': datetime.now().isoformat()
        }, room=user_id)

@socketio.on('start_analysis')
def handle_start_analysis(data):
    """Handle symptom analysis initialization"""
    user_id = session.get('user_id')
    if not user_id:
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        symptoms = data.get('symptoms', '')
        language = data.get('language', 'english')
        
        # Notify client analysis started
        emit('analysis_update', {
            'status': 'started',
            'message': 'Analyzing symptoms...',
            'timestamp': datetime.now().isoformat()
        }, room=user_id)
        
        # Simulate processing with progress updates
        for i in range(1, 4):
            time.sleep(0.5)
            emit('analysis_update', {
                'status': 'processing',
                'progress': i * 25,
                'timestamp': datetime.now().isoformat()
            }, room=user_id)
        
        # Final result
        emit('analysis_complete', {
            'status': 'complete',
            'message': 'Analysis finished',
            'timestamp': datetime.now().isoformat()
        }, room=user_id)
        
    except Exception as e:
        logger.error(f'Analysis error: {str(e)}')
        emit('error', {
            'message': 'Analysis failed',
            'details': str(e)
        }, room=user_id)

@socketio.on_error_default
def default_error_handler(e):
    """Global error handler for SocketIO events"""
    user_id = session.get('user_id')
    logger.error(f'SocketIO error: {str(e)}')
    if user_id:
        emit('error', {
            'message': 'An error occurred',
            'details': str(e)
        }, room=user_id)
