"""
SafeRoute Saheli — Database Initializer & Migration Seeder
Compatible with PostgreSQL (Render, Neon, Supabase, AWS RDS) and SQLite/MySQL.
Runs db.create_all() and seeds default admin accounts and emergency directories.
"""

import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app import create_app
from backend.app.database import db
from backend.app.models.admin import AdminUser
from backend.app.models.user import User, EmergencyContact
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.routing import SafePlace, SafeZone
from backend.app.models.device import Device

def init_database():
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    with app.app_context():
        print(f"[*] Initializing database via URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 1. Create all tables
        db.create_all()
        print("[+] All database tables created successfully.")

        # 2. Seed Superadmin Account if not exists
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            admin = AdminUser(
                username='admin',
                email='admin@saheli.org',
                role='SUPERADMIN',
                is_active=True
            )
            admin.set_password('AdminSaheli@2026')
            db.session.add(admin)
            print("[+] Seeded Superadmin account: admin / AdminSaheli@2026")
        else:
            print("[i] Superadmin account already exists.")

        # 3. Seed Demo Saheli User if not exists
        demo_user = User.query.filter_by(email='priya.sharma@saheli.org').first()
        if not demo_user:
            demo_user = User(
                name='Priya Sharma',
                email='priya.sharma@saheli.org',
                phone='+919876543210',
                emergency_blood_group='O+',
                medical_notes='Asthmatic — carry emergency inhaler',
                is_active=True,
                is_verified=True
            )
            demo_user.set_password('PriyaSaheli@2026')
            db.session.add(demo_user)
            db.session.flush()

            # Seed Emergency Contact
            contact = EmergencyContact(
                user_id=demo_user.id,
                name='Rajesh Sharma (Father)',
                phone='+919811122233',
                relationship='Father',
                priority_order=1,
                notify_sms=True,
                notify_call=True
            )
            db.session.add(contact)
            print(f"[+] Seeded Demo Saheli user: {demo_user.name} ({demo_user.email})")

        # 4. Seed Verified Safe Places (Police, Hospitals, Shelters)
        if SafePlace.query.count() == 0:
            places = [
                SafePlace(
                    name="Delhi Police Headquarters & Women Safety Cell",
                    category="POLICE_STATION",
                    latitude=28.6289,
                    longitude=77.2405,
                    address="Jai Singh Marg, Connaught Place, New Delhi",
                    phone="1091",
                    is_24x7=True,
                    is_verified=True
                ),
                SafePlace(
                    name="AIIMS Trauma Center & 24x7 Emergency",
                    category="HOSPITAL",
                    latitude=28.5672,
                    longitude=77.2100,
                    address="Ring Road, Ansari Nagar, New Delhi",
                    phone="011-26593677",
                    is_24x7=True,
                    is_verified=True
                ),
                SafePlace(
                    name="Apollo 24x7 Emergency Pharmacy",
                    category="PHARMACY",
                    latitude=28.6320,
                    longitude=77.2180,
                    address="Radial Road 3, Inner Circle, Connaught Place",
                    phone="011-41513333",
                    is_24x7=True,
                    is_verified=True
                ),
                SafePlace(
                    name="Delhi Commission for Women One-Stop Crisis Shelter",
                    category="WOMEN_SHELTER",
                    latitude=28.6250,
                    longitude=77.2310,
                    address="Vikas Bhawan, IP Estate, New Delhi",
                    phone="181",
                    is_24x7=True,
                    is_verified=True
                )
            ]
            for p in places:
                db.session.add(p)
            print(f"[+] Seeded {len(places)} Verified Safe Places.")

        # 5. Seed Geo-Fence Safe Havens
        if SafeZone.query.count() == 0 and demo_user:
            zones = [
                SafeZone(
                    user_id=demo_user.id,
                    name="IIT Delhi Campus & Hostels",
                    latitude=28.5450,
                    longitude=77.1926,
                    radius_meters=500.0,
                    curfew_start_hour=22,
                    curfew_end_hour=6,
                    is_active=True
                ),
                SafeZone(
                    user_id=demo_user.id,
                    name="Cyber City Workplace Tech Park",
                    latitude=28.4950,
                    longitude=77.0890,
                    radius_meters=600.0,
                    curfew_start_hour=21,
                    curfew_end_hour=7,
                    is_active=True
                )
            ]
            for z in zones:
                db.session.add(z)
            print(f"[+] Seeded {len(zones)} Geo-Fence Safe Havens.")

        db.session.commit()
        print("[SUCCESS] SafeRoute Saheli Database Initialization Complete!")

if __name__ == '__main__':
    init_database()
