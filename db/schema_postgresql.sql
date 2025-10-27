-- NYC Taxi Project - 3-table normalized schema (PostgreSQL 15+)
-- Created: 2025-10-13
-- Converted from MySQL to PostgreSQL for Render deployment

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
