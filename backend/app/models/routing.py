from datetime import datetime
from backend.app.database import db, generate_uuid

class SafePlace(db.Model):
    """Verified emergency shelters, police stations, hospitals, 24x7 pharmacies"""
    __tablename__ = 'safe_places'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(32), nullable=False, index=True)  # POLICE, HOSPITAL, PHARMACY, SHELTER, TRANSPORT_HUB
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    is_24x7 = db.Column(db.Boolean, default=True)
    verified_status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            'address': self.address,
            'phone_number': self.phone_number,
            'is_24x7': self.is_24x7,
            'verified_status': self.verified_status,
        }


class NearbyHelpLog(db.Model):
    """Logs when a safe place is recommended to user/guardian during emergency"""
    __tablename__ = 'nearby_help_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.String(36), db.ForeignKey('emergency_incidents.id', ondelete='CASCADE'), nullable=False)
    safe_place_id = db.Column(db.String(36), db.ForeignKey('safe_places.id', ondelete='CASCADE'), nullable=False)
    distance_meters = db.Column(db.Float, nullable=False)
    guidance_presented_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('EmergencyIncident', back_populates='nearby_help_entries')
    safe_place = db.relationship('SafePlace')


class Route(db.Model):
    """Navigation routes calculated for users"""
    __tablename__ = 'routes'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    start_lat = db.Column(db.Numeric(10, 7), nullable=False)
    start_lng = db.Column(db.Numeric(10, 7), nullable=False)
    dest_lat = db.Column(db.Numeric(10, 7), nullable=False)
    dest_lng = db.Column(db.Numeric(10, 7), nullable=False)
    route_type = db.Column(db.String(32), nullable=False)  # SHORTEST, FASTEST, SAFETY_OPTIMIZED
    polyline_geojson = db.Column(db.JSON, nullable=False)
    total_distance_km = db.Column(db.Float, nullable=False)
    estimated_duration_mins = db.Column(db.Float, nullable=False)
    overall_safety_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='routes')
    segments = db.relationship('RouteSegment', back_populates='route', cascade='all, delete-orphan')
    risk_evaluation = db.relationship('RouteRiskScore', back_populates='route', uselist=False, cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start': {'lat': float(self.start_lat), 'lng': float(self.start_lng)},
            'destination': {'lat': float(self.dest_lat), 'lng': float(self.dest_lng)},
            'route_type': self.route_type,
            'polyline_geojson': self.polyline_geojson,
            'total_distance_km': self.total_distance_km,
            'estimated_duration_mins': self.estimated_duration_mins,
            'overall_safety_score': self.overall_safety_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class RouteSegment(db.Model):
    """Segment breakdown of routes with granular scores"""
    __tablename__ = 'route_segments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route_id = db.Column(db.String(36), db.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False, index=True)
    segment_index = db.Column(db.Integer, nullable=False)
    start_lat = db.Column(db.Numeric(10, 7), nullable=False)
    start_lng = db.Column(db.Numeric(10, 7), nullable=False)
    end_lat = db.Column(db.Numeric(10, 7), nullable=False)
    end_lng = db.Column(db.Numeric(10, 7), nullable=False)
    segment_safety_score = db.Column(db.Float, nullable=False)
    lighting_score = db.Column(db.Float, default=0.5)
    crime_score = db.Column(db.Float, default=0.2)
    crowd_score = db.Column(db.Float, default=0.6)
    isolation_score = db.Column(db.Float, default=0.3)

    route = db.relationship('Route', back_populates='segments')


class RouteRiskScore(db.Model):
    """Detailed soft computing breakdown for route evaluation"""
    __tablename__ = 'route_risk_scores'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    route_id = db.Column(db.String(36), db.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False)
    neuro_fuzzy_risk = db.Column(db.Float, nullable=False)
    genetic_fitness_score = db.Column(db.Float, nullable=False)
    crime_density_factor = db.Column(db.Float, nullable=False)
    isolation_factor = db.Column(db.Float, nullable=False)
    lighting_factor = db.Column(db.Float, nullable=False)
    crowd_factor = db.Column(db.Float, nullable=False)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

    route = db.relationship('Route', back_populates='risk_evaluation')


class RouteDeviation(db.Model):
    """Log of detected path deviations"""
    __tablename__ = 'route_deviations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    route_id = db.Column(db.String(36), db.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False)
    incident_id = db.Column(db.String(36), nullable=True)
    expected_lat = db.Column(db.Numeric(10, 7), nullable=False)
    expected_lng = db.Column(db.Numeric(10, 7), nullable=False)
    actual_lat = db.Column(db.Numeric(10, 7), nullable=False)
    actual_lng = db.Column(db.Numeric(10, 7), nullable=False)
    deviation_distance_meters = db.Column(db.Float, nullable=False)
    action_taken = db.Column(db.String(128), default='RECALCULATED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RiskFeature(db.Model):
    """Spatial database of benchmark safety attributes"""
    __tablename__ = 'risk_features'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    radius_meters = db.Column(db.Float, default=200.0)
    crime_rate = db.Column(db.Float, default=0.0)
    lighting_quality = db.Column(db.Float, default=1.0)
    isolation_index = db.Column(db.Float, default=0.0)
    crowd_density = db.Column(db.Float, default=0.5)
    police_proximity_meters = db.Column(db.Float, default=1000.0)
    hospital_proximity_meters = db.Column(db.Float, default=1500.0)
    historical_incident_count = db.Column(db.Integer, default=0)
    data_source_label = db.Column(db.String(64), default='SYNTHETIC_BENCHMARK')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RiskPrediction(db.Model):
    """Inference history from AI Safety Models"""
    __tablename__ = 'risk_predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    model_type = db.Column(db.String(32), nullable=False)  # NEURO_FUZZY, GA_OPTIMIZED, ENSEMBLE
    risk_score = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    features_json = db.Column(db.JSON, nullable=True)
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)


class SafeZone(db.Model):
    """User-defined geo-fenced safe havens (Home, College, Office, Hostel)"""
    __tablename__ = 'safe_zones'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    radius_meters = db.Column(db.Float, default=150.0)
    curfew_start_hour = db.Column(db.Integer, nullable=True)
    curfew_end_hour = db.Column(db.Integer, nullable=True)
    notify_guardians_on_arrival = db.Column(db.Boolean, default=True)
    notify_guardians_on_departure = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('safe_zones', cascade='all, delete-orphan'))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'radius_meters': self.radius_meters,
            'curfew_start_hour': self.curfew_start_hour,
            'curfew_end_hour': self.curfew_end_hour,
            'notify_guardians_on_arrival': self.notify_guardians_on_arrival,
            'notify_guardians_on_departure': self.notify_guardians_on_departure,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
