"""
User Service - Business logic for user management
Handles user profiles and farms
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User, Farm


class UserService:
    """Service layer for user management"""

    @staticmethod
    async def get_or_create_user(
        firebase_uid: str,
        phone_number: Optional[str] = None,
        db: AsyncSession = None
    ) -> User:
        """
        Get existing user or create new one

        Args:
            firebase_uid: Firebase user ID
            phone_number: User phone number
            db: Database session

        Returns:
            User model instance
        """
        result = await db.execute(
            select(User).where(User.firebase_uid == firebase_uid)
        )
        user = result.scalar_one_or_none()

        if user is None:
            # Create new user
            user = User(
                firebase_uid=firebase_uid,
                phone_number=phone_number
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user

    @staticmethod
    async def get_user_by_firebase_uid(
        firebase_uid: str,
        db: AsyncSession
    ) -> Optional[User]:
        """Get user by Firebase UID"""
        result = await db.execute(
            select(User).where(User.firebase_uid == firebase_uid)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_profile(
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        language: Optional[str] = None,
        db: AsyncSession = None
    ) -> bool:
        """Update user profile"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False

        if name:
            user.name = name
        if email:
            user.email = email
        if language:
            user.language_preference = language

        await db.commit()
        return True

    @staticmethod
    async def create_farm(
        user_id: int,
        name: str,
        location: str,
        latitude: float,
        longitude: float,
        soil_type: str,
        farm_size_acres: float,
        annual_rainfall_mm: float = 0,
        avg_temperature_c: float = 25,
        db: AsyncSession = None
    ) -> Farm:
        """
        Create a new farm for user

        Args:
            user_id: User ID
            name: Farm name
            location: Location string
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            soil_type: Soil type
            farm_size_acres: Farm size in acres
            annual_rainfall_mm: Annual rainfall
            avg_temperature_c: Average temperature
            db: Database session

        Returns:
            Created farm
        """
        farm = Farm(
            user_id=user_id,
            name=name,
            location=location,
            latitude=latitude,
            longitude=longitude,
            soil_type=soil_type,
            farm_size_acres=farm_size_acres,
            annual_rainfall_mm=annual_rainfall_mm,
            avg_temperature_c=avg_temperature_c
        )
        db.add(farm)
        await db.commit()
        await db.refresh(farm)

        return farm

    @staticmethod
    async def get_user_farms(
        user_id: int,
        db: AsyncSession
    ) -> List[Farm]:
        """Get all farms for a user"""
        result = await db.execute(
            select(Farm)
            .where(Farm.user_id == user_id)
            .order_by(Farm.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_farm(
        farm_id: int,
        user_id: int,
        db: AsyncSession
    ) -> Optional[Farm]:
        """Get specific farm by ID"""
        result = await db.execute(
            select(Farm)
            .where(Farm.id == farm_id)
            .where(Farm.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_farm(
        farm_id: int,
        user_id: int,
        updates: Dict[str, Any],
        db: AsyncSession
    ) -> bool:
        """Update farm details"""
        farm = await UserService.get_farm(farm_id, user_id, db)
        if farm is None:
            return False

        allowed_fields = [
            "name", "location", "latitude", "longitude",
            "soil_type", "farm_size_acres", "annual_rainfall_mm", "avg_temperature_c"
        ]

        for field, value in updates.items():
            if field in allowed_fields and hasattr(farm, field):
                setattr(farm, field, value)

        await db.commit()
        return True

    @staticmethod
    async def delete_farm(
        farm_id: int,
        user_id: int,
        db: AsyncSession
    ) -> bool:
        """Delete a farm"""
        farm = await UserService.get_farm(farm_id, user_id, db)
        if farm is None:
            return False

        await db.delete(farm)
        await db.commit()
        return True
