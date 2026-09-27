import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.config import config_by_name
from backend.app.database import db

# SocketIO Global Instance
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

def create_app(config_name: str = None) -> Flask:
    """Application Factory for SafeRoute Saheli Backend"""
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize Extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    socketio.init_app(app)

    # Ensure Upload Directories Exist
    upload_path = app.config.get('UPLOAD_FOLDER', os.path.join(app.root_path, '..', 'uploads'))
    os.makedirs(os.path.join(upload_path, 'camera'), exist_ok=True)
    os.makedirs(os.path.join(upload_path, 'audio'), exist_ok=True)

    # Register Blueprints
    from backend.app.auth.routes import auth_bp
    from backend.app.guardian.routes import guardian_bp
    from backend.app.device.routes import device_bp
    from backend.app.emergency.routes import emergency_bp
    from backend.app.location.routes import location_bp
    from backend.app.camera.routes import camera_bp
    from backend.app.audio.routes import audio_bp
    from backend.app.routing.routes import routing_bp
    from backend.app.routes.nearby import nearby_bp
    from backend.app.ai.routes import ai_bp
    from backend.app.admin.routes import admin_bp
    from backend.app.notification.routes import notification_bp
    from backend.app.notification.firebase_admin_client import FirebaseAdminClient
    from backend.app.routes.docs import docs_bp
    from backend.app.routes.evidence import evidence_bp
    from backend.app.routes.geofence import geofence_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(guardian_bp)
    app.register_blueprint(device_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(audio_bp)
    app.register_blueprint(routing_bp)
    app.register_blueprint(nearby_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(geofence_bp)

    # Route aliases for singular/plural endpoint parity
    app.add_url_rule('/api/guardian/add', view_func=app.view_functions['guardian.add_guardian'], methods=['POST'])

    # Initialize Firebase Admin Client
    FirebaseAdminClient.initialize(app.config)

    # Register SocketIO Events
    from backend.app.websocket.events import register_socketio_events
    register_socketio_events(socketio)

    # Health Check Endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = "HEALTHY"
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception as ex:
            db_status = f"UNHEALTHY: {str(ex)}"

        return jsonify({
            'status': 'ONLINE',
            'application': app.config['APP_NAME'],
            'version': app.config['VERSION'],
            'database': db_status,
            'test_mode': app.config.get('TEST_MODE', True)
        }), 200

    # Serve static uploaded evidence files
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(upload_path, filename)

    # Enterprise Security Headers (Phase 16 Compliance)
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response


    # Automatic Table Creation & Benchmark Seeding
    with app.app_context():
        import backend.app.models  # Load all models
        db.create_all()

        # Seed initial safe places if empty
        from backend.app.models.routing import SafePlace
        if SafePlace.query.count() == 0:
            seed_places = [
                SafePlace(
                    id='sp-pol-001',
                    name='Central Women Police Assistance Booth',
                    category='POLICE',
                    latitude=28.613939,
                    longitude=77.209021,
                    address='Connaught Place Circle, New Delhi',
                    phone_number='+911123456789',
                    is_24x7=True,
                    verified_status=True
                ),
                SafePlace(
                    id='sp-pol-002',
                    name='Metro Security Police Station',
                    category='POLICE',
                    latitude=28.628900,
                    longitude=77.207500,
                    address='Barakhamba Road Metro Station, Gate 2',
                    phone_number='+911123456790',
                    is_24x7=True,
                    verified_status=True
                ),
                SafePlace(
                    id='sp-hosp-001',
                    name='City General Multi-Specialty Hospital',
                    category='HOSPITAL',
                    latitude=28.618900,
                    longitude=77.215500,
                    address='Ashoka Road, New Delhi',
                    phone_number='+911145678901',
                    is_24x7=True,
                    verified_status=True
                ),
                SafePlace(
                    id='sp-shelter-001',
                    name='Sakhi Women One Stop Center',
                    category='SHELTER',
                    latitude=28.610500,
                    longitude=77.220000,
                    address='India Gate Safe Corridor',
                    phone_number='181',
                    is_24x7=True,
                    verified_status=True
                )
            ]
            for sp in seed_places:
                db.session.add(sp)
            db.session.commit()

    return app
