"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { MapPin, Phone, Globe, Navigation, Search } from "lucide-react";

// Dynamically import MapComponent to disable SSR
const MapComponent = dynamic(() => import("./MapComponent"), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center bg-muted/30">Loading Map...</div>
});

export default function LocatorPage() {
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi("/facilities")
      .then((res) => setFacilities(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-foreground">Care Locator</h1>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search location or facility..." 
            className="pl-9 h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* List side */}
        <div className="lg:col-span-1 space-y-4 max-h-[80vh] overflow-y-auto pr-2">
          {loading ? (
            <div className="text-center py-8">Loading facilities...</div>
          ) : facilities.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground border-2 border-dashed rounded-lg">
              No facilities found in the database.
            </div>
          ) : (
            facilities.map((f: any) => (
              <Card key={f.id} className="cursor-pointer hover:border-primary transition-colors">
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <h3 className="font-semibold text-lg">{f.name}</h3>
                    <Badge variant={f.facility_type === 'hospital' ? 'default' : 'secondary'} className="capitalize">
                      {f.facility_type}
                    </Badge>
                  </div>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    {f.address && (
                      <div className="flex items-start gap-2">
                        <MapPin className="h-4 w-4 mt-0.5 shrink-0" />
                        <span>{f.address}</span>
                      </div>
                    )}
                    {f.phone && (
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 shrink-0" />
                        <span>{f.phone}</span>
                      </div>
                    )}
                    {f.website && (
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4 shrink-0" />
                        <a href={f.website} target="_blank" rel="noreferrer" className="text-primary hover:underline truncate">
                          {f.website}
                        </a>
                      </div>
                    )}
                    {f.source_url && (
                      <div className="mt-2 pt-2 border-t text-xs flex justify-between items-center text-muted-foreground">
                        <span className="truncate pr-2">Source: <a href={f.source_url} target="_blank" rel="noreferrer" className="hover:underline">{f.source_url.replace(/^https?:\/\//, '')}</a></span>
                        {f.last_verified_at && (
                          <span className="shrink-0">Verified: {new Date(f.last_verified_at).toLocaleDateString()}</span>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Map Side */}
        <div className="lg:col-span-2">
          <Card className="h-full min-h-[500px] overflow-hidden">
            <MapComponent facilities={facilities} />
          </Card>
        </div>
      </div>
    </div>
  );
}
