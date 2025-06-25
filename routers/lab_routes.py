from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, text
from typing import List, Optional, Tuple
from chatbot.config.database import get_db
from chatbot.models.lab_vendor import LabVendor
from chatbot.models.lab_vendor_addresses import LabVendorAddresses
from chatbot.models.users import Users
from chatbot.schemas.lab_vendor import NearbyLabResponse, ServicesModel
import logging
import requests
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_DISTANCE_KM = 5  # Maximum distance in kilometers

router = APIRouter()

def get_coordinates_from_pincode(pincode: str) -> Optional[Tuple[float, float]]:
    """Convert pincode to latitude and longitude using a geocoding service."""
    try:
        # Using Nominatim API for geocoding (more reliable than India Post API)
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            'postalcode': pincode,
            'country': 'India',
            'format': 'json'
        }
        headers = {
            'User-Agent': 'LabBuddy/1.0'  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if data and len(data) > 0:
            # Get the first result
            location = data[0]
            return float(location['lat']), float(location['lon'])
            
        logger.warning(f"No coordinates found for pincode {pincode}")
        return None
    except Exception as e:
        logger.error(f"Error getting coordinates for pincode {pincode}: {str(e)}")
        return None

@router.get("/nearby-labs/{pincode}", response_model=List[NearbyLabResponse])
async def get_nearby_labs(
    pincode: str,
    test_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get labs within 5km radius using Haversine formula for distance calculation.
    Optionally filter labs by test name.
    """
    try:
        logger.info(f"Searching labs for pincode: {pincode} and test_name: {test_name}")
        
        if not pincode or len(pincode) != 6:
            raise HTTPException(status_code=400, detail="Invalid pincode format. Please provide a 6-digit pincode")

        # First try to find a lab in our database with this pincode to get coordinates
        reference_query = select(Users.latitude, Users.longitude).join(
            LabVendor, LabVendor.user_id == Users.id
        ).join(
            LabVendorAddresses, LabVendor.id == LabVendorAddresses.lab_vendor_id
        ).where(
            and_(
                LabVendorAddresses.pincode == pincode,
                Users.latitude.isnot(None),
                Users.longitude.isnot(None)
            )
        ).limit(1)

        try:
            reference_result = await db.execute(reference_query)
            reference = reference_result.first()
            
            if reference and reference.latitude and reference.longitude:
                user_lat = float(reference.latitude)
                user_lon = float(reference.longitude)
                logger.info(f"Using coordinates from database for pincode {pincode}: lat={user_lat}, lon={user_lon}")
            else:
                # If no coordinates in database, try geocoding service
                coordinates = get_coordinates_from_pincode(pincode)
                if not coordinates:
                    logger.error(f"Could not get coordinates for pincode {pincode}")
                    raise HTTPException(status_code=400, detail=f"Could not get coordinates for pincode {pincode}")
                
                user_lat, user_lon = coordinates
                logger.info(f"Using geocoded coordinates for pincode {pincode}: lat={user_lat}, lon={user_lon}")
        except Exception as e:
            logger.error(f"Error getting reference coordinates: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get coordinates")

        # Optimized query: filter by test name and active labs before distance calculation
        sql = f"""
            WITH filtered_labs AS (
                SELECT 
                    lab_vendor.id,
                    lab_vendor.lab_name,
                    lab_vendor_addresses.address,
                    lab_vendor_addresses.city,
                    lab_vendor_addresses.state,
                    lab_vendor_addresses.pincode,
                    lab_vendor.pathology,
                    lab_vendor.radiology,
                    lab_vendor.lab_homecollection_charge,
                    users.latitude,
                    users.longitude
                    {', testname.name AS test_name' if test_name else ''}
                FROM lab_vendor
                JOIN lab_vendor_addresses ON lab_vendor.id = lab_vendor_addresses.lab_vendor_id
                JOIN users ON lab_vendor.user_id = users.id
                {('JOIN testpricing ON testpricing.user_id = users.id JOIN testname ON testpricing.test_name_id = testname.id' if test_name else '')}
                WHERE lab_vendor.isDeleted = false 
                AND lab_vendor.isActive = true
                AND users.latitude IS NOT NULL
                AND users.longitude IS NOT NULL
                {('AND LOWER(testname.name) LIKE LOWER(:test_name)' if test_name else '')}
            )
            , lab_distances AS (
                SELECT *,
                    (
                        6371 * 2 * ASIN(
                            SQRT(
                                POWER(SIN(RADIANS((:user_lat - latitude) / 2)), 2) +
                                COS(RADIANS(:user_lat)) * COS(RADIANS(latitude)) *
                                POWER(SIN(RADIANS((:user_lon - longitude) / 2)), 2)
                            )
                        )
                    ) as distance
                FROM filtered_labs
            )
            SELECT *
            FROM lab_distances
            WHERE distance <= {MAX_DISTANCE_KM}
            ORDER BY distance ASC
            LIMIT 50
        """

        params = {
            "user_lat": user_lat,
            "user_lon": user_lon
        }
        if test_name:
            params["test_name"] = f"%{test_name}%"

        try:
            result = await db.execute(
                text(sql),
                params
            )
            labs = result.all()
            logger.info(f"Found {len(labs)} labs within {MAX_DISTANCE_KM}km")
            
            # Debug log to check coordinates and distance calculation
            for lab in labs:
                logger.info(f"Lab {lab.id} coordinates: lat={lab.latitude}, lon={lab.longitude}, calculated distance={lab.distance:.2f}km")
                
        except Exception as db_error:
            logger.error(f"Database query error: {str(db_error)}")
            raise HTTPException(status_code=500, detail="Database query failed")

        # Format response
        nearby_labs = []
        for lab in labs:
            response_data = dict(
                id=lab.id,
                lab_name=lab.lab_name,
                address=lab.address,
                city=lab.city,
                state=lab.state,
                pincode=lab.pincode,
                distance=round(float(lab.distance), 2),
                services=ServicesModel(
                    pathology=lab.pathology,
                    radiology=lab.radiology
                ),
                home_collection_charge=float(lab.lab_homecollection_charge) if lab.lab_homecollection_charge is not None else 0.0
            )
            # If test_name filter is used, add the test name to the response (if available)
            if test_name and hasattr(lab, 'test_name'):
                response_data['test_name'] = lab.test_name
            nearby_labs.append(NearbyLabResponse(**response_data))

        logger.info(f"Returning {len(nearby_labs)} labs within {MAX_DISTANCE_KM}km")
        return nearby_labs

    except Exception as e:
        logger.error(f"Error in get_nearby_labs: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while fetching labs: {str(e)}"
        ) 