"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix leaflet marker icons in Next.js
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

interface MapComponentProps {
  facilities: any[];
}

export default function MapComponent({ facilities }: MapComponentProps) {
  // Center on Hyderabad for the live environment
  const defaultCenter: [number, number] = [17.4065, 78.4772];
  const defaultZoom = 11;

  return (
    <MapContainer 
      center={defaultCenter} 
      zoom={defaultZoom} 
      style={{ height: "100%", width: "100%", zIndex: 0 }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {facilities.map((f, i) => {
        // Fallback random positions around Hyderabad for demo facilities without lat/lng
        const lat = f.latitude || defaultCenter[0] + (Math.random() - 0.5) * 0.1;
        const lng = f.longitude || defaultCenter[1] + (Math.random() - 0.5) * 0.1;
        
        return (
          <Marker key={f.id || i} position={[lat, lng]} icon={icon}>
            <Popup>
              <div className="font-semibold">{f.name}</div>
              <div className="text-sm text-gray-600 capitalize">{f.facility_type}</div>
              <div className="text-xs mt-1">{f.address}</div>
              {f.phone && <div className="text-xs text-blue-600 mt-1">{f.phone}</div>}
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
