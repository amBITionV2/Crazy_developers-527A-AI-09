import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { User, Heart, Calendar, Droplets, Download, AlertCircle, Clock, MapPin } from 'lucide-react';

interface PatientProfileProps {
  className?: string;
}

const PatientProfile: React.FC<PatientProfileProps> = ({ className }) => {
  const handleDownloadReport = () => {
    // Mock download functionality
    const reportData = {
      patientName: "Santhosh",
      bloodType: "B+",
      condition: "Dialysis",
      requiredComponent: "Single Donor Platelet",
      frequency: "Every 3 days",
      lastTreatment: "2025-10-02",
      nextTreatment: "2025-10-05",
      totalSessions: 156,
      emergencyContacts: [
        { name: "Dr. Kumar", phone: "+91-9876543210", relation: "Nephrologist" },
        { name: "Priya Santhosh", phone: "+91-9876543211", relation: "Spouse" }
      ]
    };

    // Create and download mock PDF report
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `${reportData.patientName}_Health_Report_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Patient Basic Info */}
      <Card className="border-destructive/20 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-destructive/10 to-destructive/5 rounded-t-lg">
          <CardTitle className="flex items-center gap-2 text-destructive">
            <User className="h-5 w-5" />
            Patient Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Santhosh</h3>
                <p className="text-sm text-gray-600">Patient ID: PAT-2025-001</p>
              </div>
              <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/30">
                <Droplets className="h-3 w-3 mr-1" />
                B+
              </Badge>
            </div>
            
            <Separator />
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Heart className="h-4 w-4 text-destructive" />
                  <span className="font-medium">Condition:</span>
                </div>
                <p className="text-gray-700 ml-6">Dialysis</p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-destructive" />
                  <span className="font-medium">Frequency:</span>
                </div>
                <p className="text-gray-700 ml-6">Every 3 days</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Blood Requirements */}
      <Card className="border-destructive/30 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-destructive/10 to-destructive/5 rounded-t-lg">
          <CardTitle className="flex items-center gap-2 text-destructive">
            <Droplets className="h-5 w-5" />
            Blood Requirements
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-destructive/10 rounded-lg border border-destructive/20">
              <div>
                <p className="font-medium text-destructive">Required Component</p>
                <p className="text-sm text-destructive/80">Single Donor Platelet</p>
              </div>
              <Badge className="bg-destructive/20 text-destructive border-destructive/30">
                High Priority
              </Badge>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium text-gray-700">Blood Type</p>
                <p className="text-lg font-bold text-destructive">B+</p>
              </div>
              <div>
                <p className="font-medium text-gray-700">Compatibility</p>
                <p className="text-sm text-gray-600">B+, B-, O+, O-</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Treatment Schedule */}
      <Card className="border-primary/20 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-t-lg">
          <CardTitle className="flex items-center gap-2 text-primary">
            <Clock className="h-5 w-5" />
            Treatment Schedule
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-primary/10 rounded-lg border border-primary/20">
              <div>
                <p className="font-medium text-primary">Last Session</p>
                <p className="text-sm text-primary/80">October 2, 2025</p>
              </div>
              <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
                Completed
              </Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
              <div>
                <p className="font-medium text-orange-900">Next Session</p>
                <p className="text-sm text-orange-700">October 5, 2025</p>
              </div>
              <Badge variant="outline" className="bg-orange-100 text-orange-800 border-orange-300">
                Due Today
              </Badge>
            </div>
            
            <div className="text-center text-sm text-gray-600">
              <p>Total Sessions: <span className="font-semibold">156</span></p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Emergency Contacts */}
      <Card className="border-destructive/20 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-destructive/10 to-destructive/5 rounded-t-lg">
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            Emergency Contacts
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-3">
            <div className="p-3 bg-destructive/5 rounded-lg border border-destructive/10">
              <p className="font-medium text-destructive">Dr. Kumar</p>
              <p className="text-sm text-destructive/80">Nephrologist</p>
              <p className="text-sm text-gray-600">+91-9876543210</p>
            </div>
            <div className="p-3 bg-destructive/5 rounded-lg border border-destructive/10">
              <p className="font-medium text-destructive">Priya Santhosh</p>
              <p className="text-sm text-destructive/80">Spouse</p>
              <p className="text-sm text-gray-600">+91-9876543211</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Download Report */}
      <Card className="border-gray-200 shadow-lg">
        <CardContent className="pt-6">
          <Button 
            onClick={handleDownloadReport}
            className="w-full bg-gradient-to-r from-destructive to-destructive/80 hover:from-destructive/90 hover:to-destructive/70 text-white"
          >
            <Download className="h-4 w-4 mr-2" />
            Download Health History Report
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientProfile;