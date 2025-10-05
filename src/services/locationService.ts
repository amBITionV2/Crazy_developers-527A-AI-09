interface Location {
  lat: number;
  lng: number;
}

interface LocationError {
  code: number;
  message: string;
}

interface Place {
  place_id: string;
  name: string;
  vicinity: string;
  geometry: {
    location: Location;
  };
  rating?: number;
  types: string[];
  opening_hours?: {
    open_now: boolean;
  };
  photos?: Array<{
    photo_reference: string;
    height: number;
    width: number;
  }>;
}

class LocationService {
  // Get current position
  async getCurrentLocation(): Promise<{ success: boolean; location?: Location; error?: string }> {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve({
          success: false,
          error: 'Geolocation is not supported by this browser'
        });
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            success: true,
            location: {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            }
          });
        },
        (error: GeolocationPositionError) => {
          let errorMessage = '';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location access denied by user';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information is unavailable';
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timed out';
              break;
            default:
              errorMessage = 'An unknown error occurred';
              break;
          }
          resolve({
            success: false,
            error: errorMessage
          });
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      );
    });
  }

  // Calculate distance between two points using Haversine formula
  calculateDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
    const R = 6371; // Earth's radius in kilometers
    const dLat = this.toRadians(lat2 - lat1);
    const dLng = this.toRadians(lng2 - lng1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRadians(lat1)) *
        Math.cos(this.toRadians(lat2)) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in kilometers
  }

  private toRadians(degrees: number): number {
    return degrees * (Math.PI / 180);
  }

  // Geocode address to coordinates
  async geocodeAddress(address: string): Promise<{ success: boolean; location?: Location; error?: string }> {
    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(
          address
        )}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
      );

      const data = await response.json();

      if (data.status === 'OK' && data.results.length > 0) {
        const location = data.results[0].geometry.location;
        return {
          success: true,
          location: {
            lat: location.lat,
            lng: location.lng
          }
        };
      } else {
        return {
          success: false,
          error: 'Address not found'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to geocode address'
      };
    }
  }

  // Reverse geocode coordinates to address
  async reverseGeocode(lat: number, lng: number): Promise<{ success: boolean; address?: string; error?: string }> {
    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
      );

      const data = await response.json();

      if (data.status === 'OK' && data.results.length > 0) {
        return {
          success: true,
          address: data.results[0].formatted_address
        };
      } else {
        return {
          success: false,
          error: 'Address not found for these coordinates'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to reverse geocode coordinates'
      };
    }
  }

  // Find nearby blood banks or hospitals
  async findNearbyPlaces(
    location: Location,
    type: 'hospital' | 'blood_bank' = 'hospital',
    radius: number = 5000
  ): Promise<{ success: boolean; places?: Place[]; error?: string }> {
    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${location.lat},${location.lng}&radius=${radius}&type=${type}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
      );

      const data = await response.json();

      if (data.status === 'OK') {
        return {
          success: true,
          places: data.results
        };
      } else {
        return {
          success: false,
          error: 'No places found nearby'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to find nearby places'
      };
    }
  }

  // Request location permission
  async requestLocationPermission(): Promise<{ success: boolean; error?: string }> {
    try {
      const permission = await navigator.permissions.query({ name: 'geolocation' });
      
      if (permission.state === 'granted') {
        return { success: true };
      } else if (permission.state === 'prompt') {
        // Try to get location which will prompt user
        const result = await this.getCurrentLocation();
        return {
          success: result.success,
          error: result.error
        };
      } else {
        return {
          success: false,
          error: 'Location permission denied'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to request location permission'
      };
    }
  }
}

export const locationService = new LocationService();
export default locationService;