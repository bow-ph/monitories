from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.package import Package
from app.schemas.package import Package as PackageSchema
from app.schemas.package import PackageCreate, PackageUpdate
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["packages"])

@router.get("/", response_model=List[PackageSchema])
async def list_packages(
    db: Session = Depends(get_db)
):
    """Get all active packages"""
    packages = db.query(Package).filter(Package.is_active == True).order_by(Package.sort_order).all()
    return packages

@router.post("/", response_model=PackageSchema)
async def create_package(
    package: PackageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new package (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only administrators can create packages")
    
    db_package = Package(**package.model_dump())
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

@router.put("/{package_id}", response_model=PackageSchema)
async def update_package(
    package_id: int,
    package: PackageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a package (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only administrators can update packages")
    
    db_package = db.query(Package).filter(Package.id == package_id).first()
    if not db_package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    for field, value in package.model_dump(exclude_unset=True).items():
        setattr(db_package, field, value)
    
    db.commit()
    db.refresh(db_package)
    return db_package

@router.delete("/{package_id}")
async def delete_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a package by setting is_active to False (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only administrators can delete packages")
    
    db_package = db.query(Package).filter(Package.id == package_id).first()
    if not db_package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    db_package.is_active = False
    db.commit()
    return {"status": "success", "message": "Package deleted"}
