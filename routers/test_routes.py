from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.models.testname import TestName
from app.models.testpricing import TestPricing
from app.models.lab_vendor import LabVendor
from app.models.lab_type import LabType
from app.schemas.testname import TestNameResponse, LabVendorPricing
from sqlalchemy import select, join

router = APIRouter()

@router.get("/search", response_model=List[TestNameResponse])
async def search_tests_by_name(test_name: str, db: Session = Depends(get_db)):
    """
    Search for tests by name and return matching tests with their lab vendor IDs, pricing, and lab type
    """
    # Query to find tests that match the search term
    query = select(TestName).where(
        TestName.name.ilike(f"%{test_name}%"),
        TestName.isDeleted == False,
        TestName.isActive == True
    )
    
    # Execute the query
    result = await db.execute(query)
    tests = result.scalars().all()
    
    if not tests:
        raise HTTPException(status_code=404, detail="No tests found matching the search criteria")
    
    # For each test, get the associated lab vendor IDs and pricing
    for test in tests:
        # Get the pricing data with lab information and lab type
        vendor_query = select(
            TestPricing.name,
            TestPricing.labbuddy_share,
            TestPricing.vendor_discount,
            TestPricing.vendor_price,
            TestPricing.lb_app_price,
            LabVendor.lab_name,
            TestPricing.user_id,
            LabType.type.label('lab_type')
        ).join(
            LabVendor,
            TestPricing.user_id == LabVendor.id
        ).outerjoin(
            LabType,
            LabVendor.id == LabType.lab_id
        ).where(
            TestPricing.test_name_id == test.id,
            TestPricing.isDeleted == False,
            TestPricing.user_id.isnot(None),
            LabVendor.isDeleted == False,
            LabVendor.isActive == True
        )
        
        vendor_result = await db.execute(vendor_query)
        pricing_data = vendor_result.all()
        
        # Store lab vendor IDs
        test.lab_vendor_ids = [p[6] for p in pricing_data if p[6] is not None]
        
        # Store pricing information with lab details and type
        test.pricing = []
        for name, labbuddy_share, vendor_discount, vendor_price, lb_app_price, lab_name, _, lab_type in pricing_data:
            pricing = LabVendorPricing(
                name=name,
                lab_name=lab_name,
                labbuddy_share=labbuddy_share or 0,
                vendor_discount=vendor_discount or 0,
                vendor_price=vendor_price or 0,
                lb_app_price=lb_app_price or 0,
                lab_type=lab_type
            )
            test.pricing.append(pricing)
    
    return tests 