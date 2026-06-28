import uuid
from app import create_app
from app.models import db, User, Role, StaffProfile

app, user_datastore = create_app()

with app.app_context():
    db.create_all()

    for role_name in ["admin", "trek_staff", "trekker"]:
        if not user_datastore.find_role(role_name):
            user_datastore.create_role(name=role_name, description=role_name.capitalize())

    db.session.commit()

    if not user_datastore.find_user(email="admin@tma.com"):
        user_datastore.create_user(
            email="admin@tma.com",
            username="admin",
            full_name="Administrator",
            password="Admin@123",  # In production, use hashed passwords and environment variables
            fs_uniquifier=str(uuid.uuid4()),
            roles=["admin"],
        )
        db.session.commit()
        print("Admin user created  →  admin@tma.com / Admin@123")
    else:
        print("Admin already exists, skipping.")

    print("Database tables created successfully.")