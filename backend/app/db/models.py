from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Farm(Base):
    """Farm details for each user"""
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), default="My Farm")
    location = Column(String(200))  # City/Region name
    latitude = Column(Float)
    longitude = Column(Float)
    soil_type = Column(String(50))  # clay, sandy, loamy, silty, peaty
    farm_size_acres = Column(Float)
    annual_rainfall_mm = Column(Float)
    avg_temperature_c = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="farms")
    recommendations = relationship("Recommendation", back_populates="farm")
    crop_cycles = relationship("CropCycle", back_populates="farm")


class Recommendation(Base):
    """AI Crop Recommendations history"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"))

    # Input data
    location = Column(String(200))
    soil_type = Column(String(50))
    rainfall_mm = Column(Float)
    temperature_c = Column(Float)
    farm_size_acres = Column(Float)

    # AI Results
    recommendations_data = Column(JSON)  # List of recommended crops
    ai_insights = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    farm = relationship("Farm", back_populates="recommendations")


class DiseaseDetection(Base):
    """Crop disease detection history"""
    __tablename__ = "disease_detections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)

    # Image and detection
    image_url = Column(String(500))  # URL to stored image
    crop_type = Column(String(50))  # Optional: what crop was being checked

    # AI Detection Results
    disease_name = Column(String(100))
    confidence = Column(Float)  # 0.0 to 1.0
    severity = Column(String(20))  # low, medium, high, critical
    description = Column(Text)
    treatment_suggestions = Column(JSON)  # List of treatments
    prevention_tips = Column(JSON)  # List of prevention tips

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="disease_detections")


class MarketData(Base):
    """Cached market price data"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(50), index=True)
    region = Column(String(100), index=True)
    market_name = Column(String(100))
    price_per_kg = Column(Float)
    currency = Column(String(10), default="INR")
    price_date = Column(DateTime)
    price_trend = Column(String(20))  # rising, falling, stable
    source = Column(String(100))  # API source

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PricePrediction(Base):
    """AI Price Predictions"""
    __tablename__ = "price_predictions"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(50), index=True)
    region = Column(String(100), index=True)
    prediction_for_date = Column(DateTime)
    predicted_price_per_kg = Column(Float)
    confidence = Column(Float)
    trend = Column(String(20))  # rising, falling, stable
    ai_analysis = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

class MarketListing(Base):
    """Listings for farmers to sell crops directly to buyers"""
    __tablename__ = "market_listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_name = Column(String(100), index=True)
    quantity = Column(Float)
    unit = Column(String(20), default="Quintal")  # kg, quintal, tons
    price_per_unit = Column(Float)
    image_url = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(200))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    seller = relationship("User", back_populates="listings")


class LabourJob(Base):
    """Job postings for agricultural labour"""
    __tablename__ = "labour_jobs"

    id = Column(Integer, primary_key=True, index=True)
    poster_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), index=True)
    job_type = Column(String(50))  # Sowing, Harvesting, Cleaning, etc.
    wage_amount = Column(Float)
    wage_period = Column(String(20), default="day")  # day, hour, task
    workers_needed = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(200))
    status = Column(String(20), default="open")  # open, filled, closed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    poster = relationship("User", back_populates="jobs")


class StoreProduct(Base):
    """Inventory for the integrated Farm Store"""
    __tablename__ = "store_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    category = Column(String(50), index=True)  # Seeds, Fertilizer, Tools, Pesticides
    price = Column(Float)
    currency = Column(String(10), default="INR")
    stock_quantity = Column(Float)
    unit = Column(String(20))
    image_url = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class CropCycle(Base):
    """Tracking the lifecycle of a crop from sowing to harvest"""
    __tablename__ = "crop_cycles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    crop_name = Column(String(50), index=True)
    sowing_date = Column(DateTime)
    status = Column(String(20), default="growth")  # sowing, growth, harvest, completed
    predicted_harvest_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="crop_cycles")
    farm = relationship("Farm", back_populates="crop_cycles")


# Backward-compatible re-export of canonical User model
from app.models.user import User  # noqa: E402
