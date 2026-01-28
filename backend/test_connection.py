import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        row = cursor.fetchone()
        print("Conexión exitosa a Supabase!")
        print(f"PostgreSQL version: {row[0]}")
        
        # Ver las tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print("\nTablas disponibles:")
        for table in tables:
            print(f"  - {table[0]}")
except Exception as e:
    print(f"Error de conexión: {e}")