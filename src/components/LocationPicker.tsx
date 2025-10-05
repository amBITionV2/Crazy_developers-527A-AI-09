import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import GoogleMap from './GoogleMap';
import { locationService } from '../services/locationService';
import { MapPin, Navigation, Search } from 'lucide-react';

interface Location {
  lat: number;
  lng: number;
}

interface LocationPickerProps {
  onLocationSelect: (location: Location, address?: string) => void;
  defaultLocation?: Location;
  height?: string;
}

export const LocationPicker: React.FC<LocationPickerProps> = ({
  onLocationSelect,
  defaultLocation,
  height = '300px'
}) => {
  const [currentLocation, setCurrentLocation] = useState<Location | null>(defaultLocation || null);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [address, setAddress] = useState('');
  const [searchAddress, setSearchAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [markers, setMarkers] = useState<Array<{
    position: Location;
    title: string;
    info: string;
  }>>([]);

  const getCurrentLocation = useCallback(async () => {
    setLoading(true);
    setError('');
    
    const result = await locationService.getCurrentLocation();
    
    if (result.success && result.location) {
      setCurrentLocation(result.location);
      setSelectedLocation(result.location);
      
      // Get address for current location
      const addressResult = await locationService.reverseGeocode(
        result.location.lat,
        result.location.lng
      );
      
      if (addressResult.success && addressResult.address) {
        setAddress(addressResult.address);
      }
      
      // Add marker for current location
      setMarkers([{
        position: result.location,
        title: 'Your Current Location',
        info: addressResult.address || 'Current location'
      }]);
      
      onLocationSelect(result.location, addressResult.address);
    } else {
      setError(result.error || 'Failed to get location');
      // Default to Bangalore if location access is denied
      const defaultLoc = { lat: 12.9716, lng: 77.5946 };
      setCurrentLocation(defaultLoc);
      setSelectedLocation(defaultLoc);
    }
    
    setLoading(false);
  }, [onLocationSelect]);

  useEffect(() => {
    // Try to get user's current location on mount
    getCurrentLocation();
  }, [getCurrentLocation]);

  const handleMapClick = async (location: Location) => {
    setSelectedLocation(location);
    setLoading(true);
    
    // Get address for selected location
    const addressResult = await locationService.reverseGeocode(
      location.lat,
      location.lng
    );
    
    if (addressResult.success && addressResult.address) {
      setAddress(addressResult.address);
    }
    
    // Update markers
    setMarkers([{
      position: location,
      title: 'Selected Location',
      info: addressResult.address || `${location.lat.toFixed(6)}, ${location.lng.toFixed(6)}`
    }]);
    
    onLocationSelect(location, addressResult.address);
    setLoading(false);
  };

  const handleAddressSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchAddress.trim()) return;
    
    setLoading(true);
    setError('');
    
    const result = await locationService.geocodeAddress(searchAddress);
    
    if (result.success && result.location) {
      setSelectedLocation(result.location);
      setCurrentLocation(result.location);
      setAddress(searchAddress);
      
      // Update markers
      setMarkers([{
        position: result.location,
        title: 'Search Result',
        info: searchAddress
      }]);
      
      onLocationSelect(result.location, searchAddress);
    } else {
      setError(result.error || 'Address not found');
    }
    
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label className="text-sm font-medium">Location</Label>
        
        {/* Search Address */}
        <form onSubmit={handleAddressSearch} className="flex gap-2">
          <Input
            type="text"
            value={searchAddress}
            onChange={(e) => setSearchAddress(e.target.value)}
            placeholder="Search for an address"
            className="flex-1"
          />
          <Button 
            type="submit" 
            variant="outline" 
            disabled={loading || !searchAddress.trim()}
            size="icon"
          >
            <Search className="h-4 w-4" />
          </Button>
        </form>

        {/* Current Location Button */}
        <Button
          type="button"
          variant="outline"
          onClick={getCurrentLocation}
          disabled={loading}
          className="w-full"
        >
          <Navigation className="h-4 w-4 mr-2" />
          {loading ? 'Getting location...' : 'Use Current Location'}
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Selected Address Display */}
      {address && (
        <div className="p-3 bg-gray-50 rounded-lg">
          <div className="flex items-start gap-2">
            <MapPin className="h-4 w-4 text-gray-500 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium">Selected Location:</p>
              <p className="text-sm text-gray-600">{address}</p>
              {selectedLocation && (
                <p className="text-xs text-gray-500">
                  {selectedLocation.lat.toFixed(6)}, {selectedLocation.lng.toFixed(6)}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Map */}
      <div className="border rounded-lg overflow-hidden">
        <GoogleMap
          center={currentLocation || { lat: 12.9716, lng: 77.5946 }}
          zoom={15}
          onLocationSelect={handleMapClick}
          markers={markers}
          height={height}
          width="100%"
        />
      </div>

      <p className="text-xs text-gray-500 text-center">
        Click on the map to select a location or search for an address above
      </p>
    </div>
  );
};