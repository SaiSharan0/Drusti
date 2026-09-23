"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Plus, Search, Camera, FileDown, X } from "lucide-react";
import { Input } from "@/components/ui/Input";

export default function PatientsPage() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // New Patient Modal State
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    sex: "unknown",
    diabetes_status: "unknown"
  });

  const loadPatients = () => {
    setLoading(true);
    fetchApi("/patients")
      .then((res) => setPatients(res.data.patients))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPatients();
  }, []);

  const createScreening = async (patientId: number) => {
    try {
      const res = await fetchApi("/screenings", {
        method: "POST",
        body: JSON.stringify({ patient_id: patientId, mode: "live" }), // using live mode here now!
      });
      window.location.href = `/screenings/${res.data.id}`;
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreatePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetchApi("/patients", {
        method: "POST",
        body: JSON.stringify({
          name: formData.name,
          age: formData.age ? parseInt(formData.age) : null,
          sex: formData.sex,
          diabetes_status: formData.diabetes_status,
        }),
      });
      setShowModal(false);
      setFormData({ name: "", age: "", sex: "unknown", diabetes_status: "unknown" });
      loadPatients(); // Refresh list
    } catch (err) {
      console.error("Failed to create patient:", err);
      // Show error inline — don't use browser alert()
      window.dispatchEvent(new CustomEvent("drusti-error", { detail: "Failed to create patient. Please try again." }));
    }
  };

  const downloadPDF = (patientId: number, patientCode: string) => {
    const token = localStorage.getItem("token");
    fetch(`http://localhost:8000/api/patients/${patientId}/pdf`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(response => response.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Drusti_Report_${patientCode}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    })
    .catch(console.error);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-foreground">Patients</h1>
        <Button className="gap-2" onClick={() => setShowModal(true)}>
          <Plus className="h-4 w-4" /> New Patient
        </Button>
      </div>

      <Card>
        <CardHeader className="py-4">
          <div className="relative w-full md:w-1/3">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search patients..." 
              className="pl-9 h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground uppercase bg-muted/50 border-b">
                <tr>
                  <th className="px-4 py-3 font-medium">Patient Code</th>
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">Details</th>
                  <th className="px-4 py-3 font-medium">Diabetes Status</th>
                  <th className="px-4 py-3 font-medium">Screenings</th>
                  <th className="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {loading ? (
                  <tr><td colSpan={6} className="px-4 py-8 text-center">Loading...</td></tr>
                ) : patients.length === 0 ? (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">No patients found.</td></tr>
                ) : (
                  patients.map((p: any) => (
                    <tr key={p.id} className="hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-3 font-medium text-primary">
                        <Link href={`/patients/${p.id}`} className="hover:underline">
                          {p.patient_code}
                        </Link>
                      </td>
                      <td className="px-4 py-3 font-medium">{p.name}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {p.age ? `${p.age}y` : "-"} / {p.sex ? p.sex.charAt(0).toUpperCase() : "-"}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="outline" className="capitalize">
                          {p.diabetes_status || "Unknown"}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        {p.screening_count} 
                        {p.last_screening && <span className="text-xs text-muted-foreground ml-2">(Last: {formatDate(p.last_screening)})</span>}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex justify-end gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            title="Download PDF"
                            onClick={() => downloadPDF(p.id, p.patient_code)}
                          >
                            <FileDown className="h-4 w-4 text-muted-foreground hover:text-primary" /> 
                          </Button>
                          <Button 
                            size="sm" 
                            variant="secondary"
                            className="gap-2"
                            onClick={() => createScreening(p.id)}
                          >
                            <Camera className="h-4 w-4" /> 
                            New Screening
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* New Patient Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-md bg-card">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle>Register New Patient</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setShowModal(false)}>
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreatePatient} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Full Name</label>
                  <Input 
                    required 
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="E.g., Anjali Sharma" 
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Age</label>
                    <Input 
                      type="number" 
                      min="1" max="120"
                      value={formData.age}
                      onChange={(e) => setFormData({...formData, age: e.target.value})}
                      placeholder="E.g., 45" 
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Sex</label>
                    <select 
                      className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      value={formData.sex}
                      onChange={(e) => setFormData({...formData, sex: e.target.value})}
                    >
                      <option value="unknown">Unknown</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Diabetes Status</label>
                  <select 
                    className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    value={formData.diabetes_status}
                    onChange={(e) => setFormData({...formData, diabetes_status: e.target.value})}
                  >
                    <option value="unknown">Unknown</option>
                    <option value="none">None</option>
                    <option value="type_1">Type 1 Diabetes</option>
                    <option value="type_2">Type 2 Diabetes</option>
                    <option value="gestational">Gestational</option>
                  </select>
                </div>
                <div className="pt-4 flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
                  <Button type="submit">Register Patient</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
