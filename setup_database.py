#!/usr/bin/env python3
"""
Database Setup Script for NYC Taxi Analytics
Creates tables and loads sample data for PostgreSQL
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/nyc_taxi"
    )

def create_tables(engine):
    """Create database tables using the PostgreSQL schema"""
    logger.info("Creating database tables...")
    
    schema_sql = """
    -- Drop existing tables (careful in production)
    DROP TABLE IF EXISTS trips CASCADE;
    DROP TABLE IF EXISTS zones CASCADE;
    DROP TABLE IF EXISTS vendors CASCADE;

    -- Vendors table: taxi companies or data vendors
    CREATE TABLE vendors (
        vendor_id SERIAL PRIMARY KEY,
        vendor_code VARCHAR(50) UNIQUE,
        vendor_name VARCHAR(255),
        notes TEXT
    );

    -- Zones table: mapping to neighborhoods / geocoded cells / taxi zones
    CREATE TABLE zones (
        zone_id SERIAL PRIMARY KEY,
        zone_name VARCHAR(255),
        borough VARCHAR(255),
        centroid_lat DOUBLE PRECISION,
        centroid_lon DOUBLE PRECISION,
        shapefile_id VARCHAR(100)
    );

    -- Trips table: main facts table, normalized to reference vendors and zones
    CREATE TABLE trips (
        id BIGSERIAL PRIMARY KEY,
        vendor_id INTEGER,
        pickup_datetime TIMESTAMP NOT NULL,
        dropoff_datetime TIMESTAMP NOT NULL,
        pickup_lat DOUBLE PRECISION,
        pickup_lon DOUBLE PRECISION,
        dropoff_lat DOUBLE PRECISION,
        dropoff_lon DOUBLE PRECISION,
        pickup_zone_id INTEGER,
        dropoff_zone_id INTEGER,
        passenger_count INTEGER CHECK (passenger_count >= 0),
        trip_distance_km DOUBLE PRECISION CHECK (trip_distance_km >= 0),
        trip_duration_seconds DOUBLE PRECISION CHECK (trip_duration_seconds >= 0),
        fare_amount DOUBLE PRECISION CHECK (fare_amount >= 0),
        tip_amount DOUBLE PRECISION DEFAULT 0 CHECK (tip_amount >= 0),
        trip_speed_kmh DOUBLE PRECISION,
        fare_per_km DOUBLE PRECISION,
        tip_pct DOUBLE PRECISION,
        hour_of_day SMALLINT CHECK (hour_of_day BETWEEN 0 AND 23),
        day_of_week VARCHAR(16),
        CONSTRAINT fk_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE SET NULL ON UPDATE CASCADE,
        CONSTRAINT fk_pickup_zone FOREIGN KEY (pickup_zone_id) REFERENCES zones(zone_id) ON DELETE SET NULL ON UPDATE CASCADE,
        CONSTRAINT fk_dropoff_zone FOREIGN KEY (dropoff_zone_id) REFERENCES zones(zone_id) ON DELETE SET NULL ON UPDATE CASCADE
    );

    -- Indexes for common queries
    CREATE INDEX idx_trips_pickup_datetime ON trips (pickup_datetime);
    CREATE INDEX idx_trips_pickup_zone ON trips (pickup_zone_id);
    CREATE INDEX idx_trips_dropoff_zone ON trips (dropoff_zone_id);
    CREATE INDEX idx_trips_vendor ON trips (vendor_id);
    CREATE INDEX idx_trips_fare ON trips (fare_amount);
    CREATE INDEX idx_trips_speed ON trips (trip_speed_kmh);

    -- Optional summary view (for analytics)
    CREATE OR REPLACE VIEW trip_summary AS
    SELECT
        DATE(pickup_datetime) AS trip_date,
        COUNT(*) AS total_trips,
        ROUND(AVG(trip_distance_km), 2) AS avg_distance_km,
        ROUND(AVG(fare_amount), 2) AS avg_fare,
        ROUND(AVG(trip_duration_seconds) / 60, 1) AS avg_duration_min,
        ROUND(AVG(tip_pct), 2) AS avg_tip_pct
    FROM trips
    GROUP BY DATE(pickup_datetime)
    ORDER BY trip_date DESC;
    """
    
    with engine.connect() as conn:
        conn.execute(text(schema_sql))
        conn.commit()
    
    logger.info("✅ Database tables created successfully")

def load_sample_data(engine):
    """Load sample data from CSV files"""
    logger.info("Loading sample data...")
    
    # Check if sample data exists
    sample_file = "data/samples/samples_1000.csv"
    if not os.path.exists(sample_file):
        logger.warning(f"Sample data file not found: {sample_file}")
        logger.info("Creating sample data...")
        create_sample_data()
    
    # Load sample data
    try:
        df = pd.read_csv(sample_file)
        logger.info(f"Loaded {len(df)} sample records")
        
        # Process and insert data
        with engine.connect() as conn:
            # Insert vendors
            vendors_data = [
                {"vendor_code": "1", "vendor_name": "Creative Mobile Technologies"},
                {"vendor_code": "2", "vendor_name": "VeriFone Inc."},
                {"vendor_code": "3", "vendor_name": "Unknown Vendor"}
            ]
            
            for vendor in vendors_data:
                conn.execute(text("""
                    INSERT INTO vendors (vendor_code, vendor_name) 
                    VALUES (:vendor_code, :vendor_name)
                    ON CONFLICT (vendor_code) DO NOTHING
                """), vendor)
            
            conn.commit()
            logger.info("✅ Vendors loaded")
            
            # Insert sample trips
            trips_data = []
            for _, row in df.iterrows():
                trip = {
                    "vendor_id": 1,  # Default vendor
                    "pickup_datetime": row.get("pickup_datetime", "2024-01-01 12:00:00"),
                    "dropoff_datetime": row.get("dropoff_datetime", "2024-01-01 12:30:00"),
                    "pickup_lat": row.get("pickup_lat", 40.7589),
                    "pickup_lon": row.get("pickup_lon", -73.9851),
                    "dropoff_lat": row.get("dropoff_lat", 40.7614),
                    "dropoff_lon": row.get("dropoff_lon", -73.9776),
                    "pickup_zone_id": None,
                    "dropoff_zone_id": None,
                    "passenger_count": row.get("passenger_count", 1),
                    "trip_distance_km": row.get("trip_distance_km", 2.5),
                    "trip_duration_seconds": row.get("trip_duration_seconds", 1800),
                    "fare_amount": row.get("fare_amount", 12.50),
                    "tip_amount": row.get("tip_amount", 2.00),
                    "trip_speed_kmh": row.get("trip_speed_kmh", 15.0),
                    "fare_per_km": row.get("fare_per_km", 5.0),
                    "tip_pct": row.get("tip_pct", 0.16),
                    "hour_of_day": row.get("hour_of_day", 12),
                    "day_of_week": row.get("day_of_week", "Monday")
                }
                trips_data.append(trip)
            
            # Batch insert trips
            if trips_data:
                conn.execute(text("""
                    INSERT INTO trips (
                        vendor_id, pickup_datetime, dropoff_datetime,
                        pickup_lat, pickup_lon, dropoff_lat, dropoff_lon,
                        pickup_zone_id, dropoff_zone_id, passenger_count,
                        trip_distance_km, trip_duration_seconds, fare_amount,
                        tip_amount, trip_speed_kmh, fare_per_km, tip_pct,
                        hour_of_day, day_of_week
                    ) VALUES (
                        :vendor_id, :pickup_datetime, :dropoff_datetime,
                        :pickup_lat, :pickup_lon, :dropoff_lat, :dropoff_lon,
                        :pickup_zone_id, :dropoff_zone_id, :passenger_count,
                        :trip_distance_km, :trip_duration_seconds, :fare_amount,
                        :tip_amount, :trip_speed_kmh, :fare_per_km, :tip_pct,
                        :hour_of_day, :day_of_week
                    )
                """), trips_data)
                
                conn.commit()
                logger.info(f"✅ {len(trips_data)} sample trips loaded")
            
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        raise

def create_sample_data():
    """Create sample data if it doesn't exist"""
    import numpy as np
    import random
    from datetime import datetime, timedelta
    
    os.makedirs("data/samples", exist_ok=True)
    
    # Generate sample data
    n_samples = 1000
    data = []
    
    for i in range(n_samples):
        # Random timestamps
        base_time = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 30))
        pickup_time = base_time + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
        dropoff_time = pickup_time + timedelta(minutes=random.randint(5, 60))
        
        # Random coordinates (NYC area)
        pickup_lat = random.uniform(40.7, 40.8)
        pickup_lon = random.uniform(-74.0, -73.9)
        dropoff_lat = pickup_lat + random.uniform(-0.01, 0.01)
        dropoff_lon = pickup_lon + random.uniform(-0.01, 0.01)
        
        # Calculate distance
        distance = ((pickup_lat - dropoff_lat)**2 + (pickup_lon - dropoff_lon)**2)**0.5 * 111  # Rough km conversion
        
        data.append({
            "pickup_datetime": pickup_time.strftime("%Y-%m-%d %H:%M:%S"),
            "dropoff_datetime": dropoff_time.strftime("%Y-%m-%d %H:%M:%S"),
            "pickup_lat": round(pickup_lat, 6),
            "pickup_lon": round(pickup_lon, 6),
            "dropoff_lat": round(dropoff_lat, 6),
            "dropoff_lon": round(dropoff_lon, 6),
            "passenger_count": random.randint(1, 6),
            "trip_distance_km": round(distance, 2),
            "trip_duration_seconds": int((dropoff_time - pickup_time).total_seconds()),
            "fare_amount": round(random.uniform(5.0, 50.0), 2),
            "tip_amount": round(random.uniform(0.0, 10.0), 2),
            "trip_speed_kmh": round(distance / ((dropoff_time - pickup_time).total_seconds() / 3600), 1),
            "fare_per_km": round(random.uniform(2.0, 8.0), 2),
            "tip_pct": round(random.uniform(0.0, 0.25), 3),
            "hour_of_day": pickup_time.hour,
            "day_of_week": pickup_time.strftime("%A")
        })
    
    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv("data/samples/samples_1000.csv", index=False)
    logger.info(f"✅ Created sample data: {len(df)} records")

def verify_setup(engine):
    """Verify database setup"""
    logger.info("Verifying database setup...")
    
    with engine.connect() as conn:
        # Check tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('trips', 'vendors', 'zones')
        """))
        tables = [row[0] for row in result.fetchall()]
        
        if len(tables) == 3:
            logger.info("✅ All tables exist")
        else:
            logger.error(f"❌ Missing tables. Found: {tables}")
            return False
        
        # Check data exists
        result = conn.execute(text("SELECT COUNT(*) FROM trips"))
        trip_count = result.fetchone()[0]
        
        result = conn.execute(text("SELECT COUNT(*) FROM vendors"))
        vendor_count = result.fetchone()[0]
        
        logger.info(f"✅ Database contains {trip_count} trips and {vendor_count} vendors")
        
        if trip_count > 0:
            logger.info("🎉 Database setup complete and ready to use!")
            return True
        else:
            logger.warning("⚠️ Database is empty")
            return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting NYC Taxi Analytics Database Setup")
    
    try:
        # Get database connection
        database_url = get_database_url()
        logger.info(f"Connecting to database...")
        
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
        # Create tables
        create_tables(engine)
        
        # Load sample data
        load_sample_data(engine)
        
        # Verify setup
        if verify_setup(engine):
            logger.info("🎉 Database setup completed successfully!")
            logger.info("Your NYC Taxi Analytics API is ready to use!")
        else:
            logger.error("❌ Database setup failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
