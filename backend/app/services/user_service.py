from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Farm
from app.models.user import User


class UserService:
    @staticmethod
    async def get_user_by_firebase_uid(firebase_uid: str, db: AsyncSession) -> Optional[User]:
        result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_farm(user_id: int, name: str, location: str, latitude: float, longitude: float, soil_type: str, farm_size_acres: float, annual_rainfall_mm: float, avg_temperature_c: float, db: AsyncSession) -> Farm:
        farm = Farm(
            user_id=user_id,
            name=name,
            location=location,
            latitude=latitude,
            longitude=longitude,
            soil_type=soil_type,
            farm_size_acres=farm_size_acres,
            annual_rainfall_mm=annual_rainfall_mm,
            avg_temperature_c=avg_temperature_c,
        )
        db.add(farm)
        await db.commit()
        await db.refresh(farm)
        return farm

    @staticmethod
    async def get_user_farms(user_id: int, db: AsyncSession) -> List[Farm]:
        result = await db.execute(select(Farm).where(Farm.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def create_user_from_firebase(
        firebase_uid: str,
        email: str,
        name: Optional[str],
        phone_number: Optional[str],
        db: AsyncSession,
    ) -> User:
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name or "",
            phone_number=phone_number or "",
            language_preference="en",
            hashed_password="",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_farm(farm_id: int, user_id: int, db: AsyncSession) -> Optional[Farm]:
        result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_farm(farm_id: int, user_id: int, updates: Dict[str, Any], db: AsyncSession) -> bool:
        farm = await UserService.get_farm(farm_id, user_id, db)
        if not farm:
            return False
        for key, value in updates.items():
            setattr(farm, key, value)
        await db.commit()
        return True

    @staticmethod
    async def delete_farm(farm_id: int, user_id: int, db: AsyncSession) -> bool:
        farm = await UserService.get_farm(farm_id, user_id, db)
        if not farm:
            return False
        await db.delete(farm)
        await db.commit()
        return True
