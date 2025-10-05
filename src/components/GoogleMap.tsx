import React, { useEffect, useRef, useState } from 'react';

interface Location {
  lat: number;
  lng: number;
}

interface GoogleMapProps {
  center?: Location;
  zoom?: number;
  onLocationSelect?: (location: Location) => void;
  markers?: Array<{
    position: Location;
    title?: string;
    info?: string;
  }>;
  height?: string;
  width?: string;
}

// Google Maps API type definitions
interface GoogleMapsAPI {
  maps: {
    Map: new (element: HTMLElement, options: GoogleMapOptions) => GoogleMapInstance;
    Marker: new (options: MarkerOptions) => MarkerInstance;
    InfoWindow: new (options: InfoWindowOptions) => InfoWindowInstance;
  };
}

interface GoogleMapOptions {
  center: Location;
  zoom: number;
  mapTypeControl?: boolean;
  streetViewControl?: boolean;
  fullscreenControl?: boolean;
}

interface GoogleMapInstance {
  addListener: (event: string, callback: (event: MapClickEvent) => void) => void;
}

interface MarkerOptions {
  position: Location;
  map: GoogleMapInstance;
  title?: string;
}

interface MarkerInstance {
  addListener: (event: string, callback: () => void) => void;
  setMap: (map: GoogleMapInstance | null) => void;
}

interface InfoWindowOptions {
  content: string;
}

interface InfoWindowInstance {
  open: (map: GoogleMapInstance, marker: MarkerInstance) => void;
}

interface MapClickEvent {
  latLng: {
    lat: () => number;
    lng: () => number;
  };
}

declare global {
  interface Window {
    google: GoogleMapsAPI;
    initMap: () => void;
  }
}

const GoogleMap: React.FC<GoogleMapProps> = ({
  center = { lat: 12.9716, lng: 77.5946 }, // Default to Bangalore
  zoom = 12,
  onLocationSelect,
  markers = [],
  height = '400px',
  width = '100%'
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<GoogleMapInstance | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const markersRef = useRef<MarkerInstance[]>([]);

  // Load Google Maps script
  useEffect(() => {
    const loadGoogleMaps = () => {
      if (window.google) {
        setIsLoaded(true);
        return;
      }

      // Check if script is already being loaded
      const existingScript = document.querySelector('script[src*="maps.googleapis.com"]');
      if (existingScript) {
        existingScript.addEventListener('load', () => setIsLoaded(true));
        return;
      }

      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}&libraries=places`;
      script.async = true;
      script.onload = () => setIsLoaded(true);
      script.onerror = () => {
        console.error('Failed to load Google Maps script');
      };
      document.head.appendChild(script);
    };

    loadGoogleMaps();
  }, []);

  // Initialize map when Google Maps is loaded
  useEffect(() => {
    if (!isLoaded || !mapRef.current) return;

    const mapInstance = new window.google.maps.Map(mapRef.current, {
      center,
      zoom,
      mapTypeControl: true,
      streetViewControl: true,
      fullscreenControl: true,
    });

    setMap(mapInstance);

    // Add click listener for location selection
    if (onLocationSelect) {
      mapInstance.addListener('click', (event: MapClickEvent) => {
        const lat = event.latLng.lat();
        const lng = event.latLng.lng();
        onLocationSelect({ lat, lng });
      });
    }
  }, [isLoaded, center, zoom, onLocationSelect]);

  // Add markers when they change
  useEffect(() => {
    if (!map) return;

    // Clear existing markers
    markersRef.current.forEach(marker => {
      if (marker.setMap) {
        marker.setMap(null);
      }
    });
    markersRef.current = [];

    // Add new markers
    if (markers.length > 0) {
      markers.forEach(marker => {
        const mapMarker = new window.google.maps.Marker({
          position: marker.position,
          map,
          title: marker.title,
        });

        markersRef.current.push(mapMarker);

        if (marker.info) {
          const infoWindow = new window.google.maps.InfoWindow({
            content: marker.info,
          });

          mapMarker.addListener('click', () => {
            infoWindow.open(map, mapMarker);
          });
        }
      });
    }

    // Cleanup function
    return () => {
      markersRef.current.forEach(marker => {
        if (marker.setMap) {
          marker.setMap(null);
        }
      });
      markersRef.current = [];
    };
  }, [map, markers]);

  if (!isLoaded) {
    return (
      <div 
        style={{ height, width }}
        className="flex items-center justify-center bg-gray-100 rounded-lg"
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading map...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={mapRef} 
      style={{ height, width }}
      className="rounded-lg border border-gray-300"
    />
  );
};

export default GoogleMap;