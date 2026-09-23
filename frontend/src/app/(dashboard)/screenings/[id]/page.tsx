"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchApi, API_BASE_URL } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { AlertCircle, Camera, CheckCircle, ChevronLeft, Info, UploadCloud } from "lucide-react";
import { Textarea } from "@/components/ui/Textarea";

export default function ScreeningPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Review states
  const [reviewAssessment, setReviewAssessment] = useState("");
  const [reviewRecommendation, setReviewRecommendation] = useState("");
  const [savingReview, setSavingReview] = useState(false);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const res = await fetchApi(`/screenings/${id}`);
      setData(res.data);
      if (res.data.review) {
        setReviewAssessment(res.data.review.clinical_assessment || "");
        setReviewRecommendation(res.data.review.final_recommendation || "");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setErrorMsg(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetchApi(`/screenings/${id}/upload`, {
        method: "POST",
        body: formData,
      });
      await loadData();
    } catch (err: any) {
      const msg = err?.detail?.message || err?.message || "Upload failed. Please try again.";
      setErrorMsg(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setErrorMsg(null);
    try {
      await fetchApi(`/screenings/${id}/analyze`, { method: "POST" });
      await loadData();
    } catch (err: any) {
      const msg = err?.detail?.message || err?.message || "Analysis failed. Please try again.";
      setErrorMsg(msg);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSaveReview = async () => {
    setSavingReview(true);
    setErrorMsg(null);
    try {
      await fetchApi(`/screenings/${id}/review`, {
        method: "POST",
        body: JSON.stringify({
          clinical_assessment: reviewAssessment,
          final_recommendation: reviewRecommendation,
        }),
      });
      router.push("/patients");
    } catch (err: any) {
      setErrorMsg("Failed to save review. Please try again.");
    } finally {
      setSavingReview(false);
    }
  };

  if (loading) return <div className="animate-pulse flex space-x-4">Loading screening details...</div>;
  if (!data) return <div>Screening not found.</div>;

  const { screening, patient, image, classification, quality, decision, lesions, explanation } = data;
  const isCreated = screening.status === "created";
  const isUploaded = screening.status === "uploaded";
  const isAnalyzed = ["completed", "reviewed", "quality_failed"].includes(screening.status);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
          Screening
          <Badge variant="outline" className="ml-2 font-mono">{screening.id}</Badge>
        </h1>
      </div>

      {errorMsg && (
        <div className="flex items-start gap-3 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <div className="flex-1">
            <p className="font-medium">An error occurred</p>
            <p className="mt-0.5">{errorMsg}</p>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-destructive/70 hover:text-destructive font-medium text-xs">Dismiss</button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column: Patient & Image */}
        <div className="space-y-6 md:col-span-1">
          <Card>
            <CardHeader className="py-4 border-b bg-muted/20">
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Patient Details</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div>
                <p className="text-lg font-semibold">{patient.name}</p>
                <a href="/patients" className="text-sm font-mono text-primary hover:underline" title="View Patient Details">{patient.patient_code}</a>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-muted-foreground text-xs">Age / Sex</p>
                  <p>{patient.age || "-"}y / {patient.sex || "-"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Diabetes</p>
                  <p className="capitalize">{patient.diabetes_status || "-"}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="py-4 border-b bg-muted/20">
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Retinal Fundus Image</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 flex flex-col items-center justify-center p-6">
              {!image ? (
                <div className="w-full">
                  <input 
                    type="file" 
                    accept="image/jpeg,image/png" 
                    className="hidden" 
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                  />
                  <div 
                    className="border-2 border-dashed border-primary/30 rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-primary/5 transition-colors"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <UploadCloud className="h-10 w-10 text-primary mb-3" />
                    <p className="text-sm font-medium text-foreground mb-1">Click to upload fundus image</p>
                    <p className="text-xs text-muted-foreground">JPEG, PNG up to 10MB</p>
                    {uploading && <p className="text-sm text-primary mt-2 font-medium">Uploading...</p>}
                  </div>
                </div>
              ) : (
                <div className="space-y-4 w-full">
                  <div className="relative rounded-lg overflow-hidden border shadow-sm aspect-square bg-black flex items-center justify-center">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src={`${API_BASE_URL}/screenings/${screening.id}/image?t=${new Date().getTime()}`} 
                      alt="Fundus" 
                      className="max-w-full max-h-full object-contain"
                    />
                  </div>
                  {explanation?.image_url && (
                    <div className="mt-4">
                      <p className="text-xs text-muted-foreground mb-2 font-medium">AI Attention Map (Grad-CAM)</p>
                      <div className="relative rounded-lg overflow-hidden border shadow-sm aspect-square bg-black flex items-center justify-center">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img 
                          src={`${API_BASE_URL.replace('/api', '')}${explanation.image_url}?t=${new Date().getTime()}`} 
                          alt="Grad-CAM" 
                          className="max-w-full max-h-full object-contain"
                        />
                      </div>
                    </div>
                  )}
                  {isUploaded && (
                    <Button 
                      className="w-full" 
                      onClick={handleAnalyze} 
                      disabled={analyzing}
                    >
                      {analyzing ? "Analyzing..." : "Run AI Analysis"}
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Results & Review */}
        <div className="space-y-6 md:col-span-2">
          
          {/* Pre-analysis state */}
          {!isAnalyzed && (
            <div className="h-full flex items-center justify-center border-2 border-dashed rounded-xl p-12 text-center bg-muted/10">
              <div className="max-w-xs space-y-4">
                <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  <Info className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold">Awaiting Analysis</h3>
                <p className="text-sm text-muted-foreground">
                  {isCreated ? "Upload a retinal fundus image to begin." : "Image uploaded. Click 'Run AI Analysis' to proceed."}
                </p>
              </div>
            </div>
          )}

          {/* Analysis Results */}
          {isAnalyzed && (
            <>
              {/* Decision Card */}
              <Card className={`border-l-4 ${
                decision?.decision === "clear" ? "border-l-success" : 
                decision?.decision === "refer" ? "border-l-warning" : "border-l-destructive"
              }`}>
                <CardHeader className="pb-3">
                  <CardTitle className="flex justify-between items-center">
                    <span>Screening Recommendation</span>
                    <Badge variant={
                      decision?.decision === "clear" ? "success" : 
                      decision?.decision === "refer" ? "warning" : "destructive"
                    } className="text-sm uppercase tracking-wider py-1 px-3">
                      {decision?.decision || "Unknown"}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm font-medium">{decision?.reason}</p>
                  {decision?.decision === "escalate" && (
                    <p className="text-xs text-muted-foreground mt-2 border-t pt-2">
                      * Escalate indicates that the AI is uncertain or image quality is poor. Clinical review is required.
                    </p>
                  )}
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Image Quality */}
                <Card>
                  <CardHeader className="py-3 border-b bg-muted/20">
                    <CardTitle className="text-sm">Image Quality Gate</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Status</span>
                      <Badge variant={quality?.status === "good" ? "success" : "destructive"}>
                        {quality?.status === "good" ? "Acceptable" : "Poor / Rejected"}
                      </Badge>
                    </div>
                    {quality?.status === "poor" && quality?.reasons && (
                      <div className="p-3 bg-destructive/10 rounded-md text-sm text-destructive">
                        <span className="font-semibold block mb-1">Issues detected:</span>
                        <ul className="list-disc pl-4">
                          {quality.reasons.map((r: string) => (
                            <li key={r} className="capitalize">{r.replace(/_/g, " ")}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* AI Classification */}
                {classification && (
                  <Card>
                    <CardHeader className="py-3 border-b bg-muted/20">
                      <CardTitle className="text-sm">Classification Results</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Predicted Grade</span>
                        <span className="font-bold text-lg text-primary">{classification.predicted_label}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Confidence</span>
                        <span>{(classification.confidence * 100).toFixed(1)}%</span>
                      </div>
                      
                      <div className="space-y-1 mt-4">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-2">Probability Distribution</span>
                        {[0, 1, 2, 3, 4].map((grade) => {
                          const prob = classification.probabilities[`grade_${grade}`] || 0;
                          return (
                            <div key={grade} className="flex items-center gap-2 text-xs">
                              <span className="w-16">Grade {grade}</span>
                              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-primary" 
                                  style={{ width: `${Math.max(prob * 100, 1)}%` }}
                                />
                              </div>
                              <span className="w-8 text-right">{(prob * 100).toFixed(0)}%</span>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Lesion Evidence */}
              {lesions && lesions.length > 0 && lesions.some((l: any) => l.status !== "not_configured") && (
                <Card>
                  <CardHeader className="py-3 border-b bg-muted/20">
                    <CardTitle className="text-sm">Detected Lesions</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4 grid grid-cols-2 gap-4">
                    {lesions.map((l: any) => (
                      <div key={l.lesion_type} className="flex items-center justify-between p-2 border rounded-md">
                        <span className="text-sm font-medium">{l.lesion_type}</span>
                        <Badge variant={
                          l.status === "detected" ? "warning" : 
                          l.status === "not_detected" ? "outline" : "secondary"
                        }>
                          {l.status.replace(/_/g, " ")}
                        </Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Clinician Review */}
              <Card className="border-primary/20 shadow-md">
                <CardHeader className="bg-primary/5 pb-4">
                  <CardTitle className="text-primary flex items-center gap-2">
                    <CheckCircle className="h-5 w-5" />
                    Clinician Review
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    Add clinical assessment and final recommendations here.
                  </p>
                </CardHeader>
                <CardContent className="pt-6 space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Clinical Assessment</label>
                    <Textarea 
                      placeholder="Enter clinical findings..." 
                      value={reviewAssessment}
                      onChange={(e) => setReviewAssessment(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Final Recommendation</label>
                    <select 
                      className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                      value={reviewRecommendation}
                      onChange={(e) => setReviewRecommendation(e.target.value)}
                    >
                      <option value="">Select recommendation...</option>
                      <option value="routine">Routine Monitoring (Clear)</option>
                      <option value="referral">Specialist Referral</option>
                      <option value="urgent_referral">Urgent Specialist Referral</option>
                      <option value="recapture">Recapture Image</option>
                    </select>
                  </div>
                </CardContent>
                <CardFooter className="bg-muted/10 border-t justify-end">
                  <Button onClick={handleSaveReview} disabled={savingReview}>
                    {savingReview ? "Saving..." : "Save Review & Finalize"}
                  </Button>
                </CardFooter>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
