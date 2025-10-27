#!/usr/bin/env python3
"""
Test script to verify database setup
"""

import os
import sys
from sqlalchemy import create_engine, text

def test_database():
    """Test database connection and data"""
    try:
        # Get database URL
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@localhost:5432/nyc_taxi"
        )
        
        print(f"🔍 Testing database connection...")
        print(f"Database URL: {database_url[:50]}...")
        
        # Connect to database
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            print(f"✅ Database connection successful: {test_value}")
            
            # Check tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('trips', 'vendors', 'zones')
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Tables found: {tables}")
            
            # Check data counts
            result = conn.execute(text("SELECT COUNT(*) FROM trips"))
            trip_count = result.fetchone()[0]
            print(f"✅ Trips count: {trip_count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM vendors"))
            vendor_count = result.fetchone()[0]
            print(f"✅ Vendors count: {vendor_count}")
            
            # Test a sample query
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_trips,
                    ROUND(AVG(trip_distance_km), 2) as avg_distance,
                    ROUND(AVG(fare_amount), 2) as avg_fare
                FROM trips
            """))
            stats = result.fetchone()
            print(f"✅ Sample stats: {stats[0]} trips, avg distance: {stats[1]}km, avg fare: ${stats[2]}")
            
            if trip_count > 0:
                print("🎉 Database setup is working perfectly!")
                return True
            else:
                print("⚠️ Database is empty - no trips found")
                return False
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
