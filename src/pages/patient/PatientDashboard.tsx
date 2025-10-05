import { useState, useEffect } from 'react';
import { Heart, AlertTriangle, Calendar, Activity, MessageCircle, LogOut, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { BloodCells } from '@/components/BloodCells';
import { LanguageSelector } from '@/components/LanguageSelector';
import { VoiceAssistant } from '@/components/VoiceAssistant';
import { AIChat } from '@/components/AIChat';
import PatientProfile from '@/components/PatientProfile';
import MockDonorResponse from '@/components/MockDonorResponse';
import { useLanguage } from '@/contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';
import { useWebSocket, WebSocketMessage, DonorResponse } from '@/services/websocketService';
import { emergencyAPI } from '@/lib/api';
import { toast } from 'sonner';

export const PatientDashboard = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const websocket = useWebSocket();
  const [activeTab, setActiveTab] = useState('sos');
  const [searching, setSearching] = useState(false);
  const [showMockDonors, setShowMockDonors] = useState(false);
  
  // SOS Form State
  const [sosFormData, setSosFormData] = useState({
    bloodComponent: '',
    patientName: '',
    hospitalName: '',
    bloodType: '',
    urgencyLevel: '',
    unitsRequired: '',
    additionalInfo: ''
  });
  
  const [donorsFound, setDonorsFound] = useState<Array<{
    name: string;
    distance: string;
    area: string;
    bloodGroup: string;
    phone: string;
  }>>([]);
  const [scheduledDonations, setScheduledDonations] = useState<Array<{
    donor: string;
    area: string;
    date: string;
    status: string;
  }>>([]);
  const [wsConnected, setWsConnected] = useState(false);

  // WebSocket message handler for donor responses
  const handleWebSocketMessage = (message: WebSocketMessage) => {
    console.log('📨 Patient received WebSocket message:', message);
    
    if (message.type === 'donor_response') {
      const responseData = message.data as DonorResponse;
      
      if (responseData.response === 'accepted') {
        // Add to scheduled donations
        const newDonation = {
          donor: responseData.donor_name,
          area: 'Location pending',
          date: new Date().toISOString().split('T')[0],
          status: 'confirmed'
        };
        
        setScheduledDonations(prev => [newDonation, ...prev]);
        
        // Show success notification
        toast.success(`✅ ${responseData.donor_name} accepted your request! Contact: ${responseData.donor_phone}`, {
          duration: 10000,
          action: {
            label: 'View',
            onClick: () => setActiveTab('future')
          }
        });
      }
    } else if (message.type === 'connection_status') {
      const statusData = message.data as Record<string, unknown>;
      setWsConnected(statusData.status === 'connected');
    }
  };

  // Connect WebSocket when component mounts
  useEffect(() => {
    const userId = localStorage.getItem('userId');
    const authToken = localStorage.getItem('authToken');
    
    // Check if user is authenticated
    if (!userId || !authToken) {
      navigate('/select-user');
      return;
    }
    
    if (userId) {
      websocket.connect(userId);
      websocket.addMessageHandler(handleWebSocketMessage);
    }

    return () => {
      websocket.removeMessageHandler(handleWebSocketMessage);
    };
  }, [websocket, navigate]);

  const handleContactDonor = (donorId: string) => {
    toast.success(`📞 Contacting donor ${donorId}...`);
    setTimeout(() => {
      toast.info(`✅ Donor ${donorId} has been notified and will respond shortly!`);
    }, 2000);
  };

  const handleSOS = async () => {
    // Validate required fields
    if (!sosFormData.bloodComponent || !sosFormData.bloodType || !sosFormData.urgencyLevel) {
      toast.error('Please fill in all required fields: Blood Component, Blood Type, and Urgency Level');
      return;
    }
    
    setSearching(true);
    
    try {
      // Show mock donor response for demo
      setTimeout(() => {
        setShowMockDonors(true);
        setSearching(false);
        toast.success(`🚨 SOS Alert Activated! Found 2 highly compatible donors for ${sosFormData.bloodComponent} (${sosFormData.bloodType})`);
      }, 3000);
      
      // Get user data from localStorage
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      
      // Create SOS alert with enhanced eRaktkosh integration format
      const sosData = {
        patient_name: sosFormData.patientName || userData.name || 'Emergency Patient',
        blood_group: sosFormData.bloodType || userData.blood_group || 'O+',
        urgency_level: sosFormData.urgencyLevel as 'CRITICAL' | 'HIGH' | 'MEDIUM',
        state: 'Karnataka',  // Should be from user profile or form
        district: 'Bangalore',  // Should be from user profile or form
        hospital_name: sosFormData.hospitalName || 'Emergency Hospital',
        hospital_address: 'Emergency Location - Bangalore',
        contact_number: userData.phone || '+91 98765 43210',
        units_needed: parseInt(sosFormData.unitsRequired) || 1,
        additional_info: `Blood Component Required: ${sosFormData.bloodComponent}. ${sosFormData.additionalInfo || 'Emergency blood requirement - urgent'}`,
        patient_age: userData.age || 30,
        medical_condition: `Requires ${sosFormData.bloodComponent} - ${sosFormData.urgencyLevel} priority. Emergency blood transfusion required.`,
        blood_component_type: sosFormData.bloodComponent, // New field for blood component specification
        component_specification: {
          type: sosFormData.bloodComponent,
          units_requested: parseInt(sosFormData.unitsRequired) || 1,
          urgency: sosFormData.urgencyLevel,
          special_requirements: sosFormData.additionalInfo
        }
      };
      
      console.log('Sending enhanced eRaktkosh SOS data:', sosData);
      
      // Uncomment below for real API call
      /*
      const response = await emergencyAPI.sendSOS(sosData);
      
      if (response.status === 'SUCCESS' || response.status === 'LIMITED_AVAILABILITY') {
        // Count total available sources
        const eraktkoshBanks = response.eraktkosh_data?.blood_availability?.blood_banks || [];
        const localDonors = response.local_donors || [];
        const totalSources = eraktkoshBanks.length + localDonors.length;
        
        // Transform local donors to match the expected interface
        const transformedDonors = localDonors.map(donor => ({
          name: donor.name,
          distance: "N/A", // Would need geolocation calculation
          area: donor.location,
          bloodGroup: donor.blood_group,
          phone: donor.phone,
          isAvailable: donor.availability_status === 'AVAILABLE'
        }));
        
        setDonorsFound(transformedDonors);
        
        // Create enhanced success message with blood component info
        let successMessage = `🚨 SOS Alert Activated! (ID: ${response.sos_id})\n`;
        successMessage += `🩸 Component: ${sosFormData.bloodComponent}\n`;
        successMessage += `🩸 Blood Type: ${sosFormData.bloodType} | Units: ${sosFormData.unitsRequired || 1}\n`;
        successMessage += `📊 Found ${totalSources} potential sources:\n`;
        if (eraktkoshBanks.length > 0) {
          successMessage += `🏥 ${eraktkoshBanks.length} blood banks via eRaktkosh\n`;
        }
        if (localDonors.length > 0) {
          successMessage += `👥 ${localDonors.length} local registered donors\n`;
        }
        
        toast.success(successMessage);
        
        // Show emergency actions
        if (response.emergency_actions && response.emergency_actions.length > 0) {
          response.emergency_actions.slice(0, 3).forEach((action, index) => {
            setTimeout(() => {
              toast.info(`📋 Action ${index + 1}: ${action}`);
            }, 1000 * (index + 1));
          });
        }
        
        // Log eRaktkosh data for debugging
        console.log('eRaktkosh Response:', response.eraktkosh_data);
        
      } else {
        toast.error(`SOS Alert failed: ${response.message}`);
      }
      */
    } catch (error) {
      console.error('SOS error:', error);
      if (error instanceof Error) {
        const errorMsg = error.message.includes('Network Error') 
          ? '🌐 Network Error: Check internet connection or backend server status'
          : `SOS failed: ${error.message}`;
        toast.error(errorMsg);
      } else {
        toast.error('Failed to send SOS alert - please check network connection');
      }
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <BloodCells />
      
      <header className="relative z-10 bg-card/30 backdrop-blur-sm border-b border-primary/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center">
              <Heart className="w-5 h-5 text-white fill-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-primary">{t('appName')}</h1>
              <p className="text-sm text-muted-foreground">{t('patient')} {t('dashboard')}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-xs text-muted-foreground">
                {wsConnected ? 'Real-time responses active' : 'Connecting...'}
              </span>
            </div>
            <LanguageSelector />
            <Button variant="outline" size="sm" onClick={() => {
              // Clear authentication data
              localStorage.removeItem('authToken');
              localStorage.removeItem('user');
              localStorage.removeItem('userId');
              navigate('/');
            }} className="border-primary/20">
              <LogOut className="w-4 h-4 mr-2" />Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="relative z-10 container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - Left 2/3 */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="bg-card/50 backdrop-blur-sm border border-primary/20 p-1 grid grid-cols-2 lg:grid-cols-4 gap-2">
                <TabsTrigger value="sos" className="data-[state=active]:bg-primary data-[state=active]:text-white">
                  <AlertTriangle className="w-4 h-4 mr-2" />{t('sosAlert')}
                </TabsTrigger>
                <TabsTrigger value="future" className="data-[state=active]:bg-primary data-[state=active]:text-white">
                  <Calendar className="w-4 h-4 mr-2" />{t('futureRequest')}
                </TabsTrigger>
                <TabsTrigger value="health" className="data-[state=active]:bg-primary data-[state=active]:text-white">
                  <Activity className="w-4 h-4 mr-2" />{t('healthMonitor')}
                </TabsTrigger>
                <TabsTrigger value="chat" className="data-[state=active]:bg-primary data-[state=active]:text-white">
                  <MessageCircle className="w-4 h-4 mr-2" />AI Chat
                </TabsTrigger>
              </TabsList>

          <TabsContent value="sos" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader>
                <CardTitle className="text-destructive">Emergency SOS Alert</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Blood Component Specification Section */}
                <div className="bg-destructive/10 p-4 rounded-lg border border-destructive/20">
                  <h3 className="text-lg font-semibold text-destructive mb-4">Blood Component Specification</h3>
                  <div className="space-y-6">
                    <div>
                      <Label className="text-sm font-medium">Select Blood Component</Label>
                      <Select value={sosFormData.bloodComponent} onValueChange={(value) => setSosFormData({...sosFormData, bloodComponent: value})}>
                        <SelectTrigger className="bg-background/50 border-primary/20 mt-1">
                          <SelectValue placeholder="Choose blood component needed" />
                        </SelectTrigger>
                        <SelectContent className="max-h-60">
                          <SelectItem value="whole-blood">Whole Blood</SelectItem>
                          <SelectItem value="single-donor-platelet">Single Donor Platelet</SelectItem>
                          <SelectItem value="single-donor-plasma">Single Donor Plasma</SelectItem>
                          <SelectItem value="sagm-packed-rbc">SAGM Packed Red Blood Cells</SelectItem>
                          <SelectItem value="random-donor-platelets">Random Donor Platelets</SelectItem>
                          <SelectItem value="platelet-rich-plasma">Platelet Rich Plasma</SelectItem>
                          <SelectItem value="platelet-concentrate">Platelet Concentrate</SelectItem>
                          <SelectItem value="plasma">Plasma</SelectItem>
                          <SelectItem value="packed-rbc">Packed Red Blood Cells</SelectItem>
                          <SelectItem value="leukoreduced-rbc">Leukoreduced RBC</SelectItem>
                          <SelectItem value="irradiated-rbc">Irradiated RBC</SelectItem>
                          <SelectItem value="fresh-frozen-plasma">Fresh Frozen Plasma</SelectItem>
                          <SelectItem value="cryoprecipitate">Cryoprecipitate</SelectItem>
                          <SelectItem value="cryo-poor-plasma">Cryo Poor Plasma</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Patient Name</Label>
                    <Input 
                      placeholder="Enter patient name" 
                      className="bg-background/50 border-primary/20" 
                      value={sosFormData.patientName}
                      onChange={(e) => setSosFormData({...sosFormData, patientName: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Hospital</Label>
                    <Input 
                      placeholder="Hospital name" 
                      className="bg-background/50 border-primary/20" 
                      value={sosFormData.hospitalName}
                      onChange={(e) => setSosFormData({...sosFormData, hospitalName: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Blood Type</Label>
                    <Select value={sosFormData.bloodType} onValueChange={(value) => setSosFormData({...sosFormData, bloodType: value})}>
                      <SelectTrigger className="bg-background/50 border-primary/20">
                        <SelectValue placeholder="Select blood type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="A+">A+ (A Positive)</SelectItem>
                        <SelectItem value="A-">A- (A Negative)</SelectItem>
                        <SelectItem value="B+">B+ (B Positive)</SelectItem>
                        <SelectItem value="B-">B- (B Negative)</SelectItem>
                        <SelectItem value="AB+">AB+ (AB Positive)</SelectItem>
                        <SelectItem value="AB-">AB- (AB Negative)</SelectItem>
                        <SelectItem value="O+">O+ (O Positive)</SelectItem>
                        <SelectItem value="O-">O- (O Negative)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Urgency Level</Label>
                    <Select value={sosFormData.urgencyLevel} onValueChange={(value) => setSosFormData({...sosFormData, urgencyLevel: value})}>
                      <SelectTrigger className="bg-background/50 border-primary/20">
                        <SelectValue placeholder="Select urgency" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="CRITICAL">🚨 Critical - Immediate Need</SelectItem>
                        <SelectItem value="HIGH">⚠️ High - Urgent (within 6 hours)</SelectItem>
                        <SelectItem value="MEDIUM">📋 Medium - Required (within 24 hours)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Units Required</Label>
                    <Select value={sosFormData.unitsRequired} onValueChange={(value) => setSosFormData({...sosFormData, unitsRequired: value})}>
                      <SelectTrigger className="bg-background/50 border-primary/20">
                        <SelectValue placeholder="Number of units" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 Unit</SelectItem>
                        <SelectItem value="2">2 Units</SelectItem>
                        <SelectItem value="3">3 Units</SelectItem>
                        <SelectItem value="4">4 Units</SelectItem>
                        <SelectItem value="5">5 Units</SelectItem>
                        <SelectItem value="6+">6+ Units (specify in notes)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Additional Information</Label>
                    <Input 
                      placeholder="Medical condition, special requirements..." 
                      className="bg-background/50 border-primary/20" 
                      value={sosFormData.additionalInfo}
                      onChange={(e) => setSosFormData({...sosFormData, additionalInfo: e.target.value})}
                    />
                  </div>
                </div>
                <Button onClick={handleSOS} className="w-full bg-destructive hover:bg-destructive/90 text-white py-6 text-lg animate-pulse-glow">
                  <AlertTriangle className="w-5 h-5 mr-2" />Send SOS Alert
                </Button>
                
                {/* Search Animation */}
                {searching && (
                  <div className="p-6 bg-primary/10 rounded-lg text-center space-y-4">
                    <MapPin className="w-12 h-12 mx-auto text-primary animate-pulse" />
                    <p className="text-lg font-semibold">Searching for donors within 1-5 km radius...</p>
                    <p className="text-sm text-muted-foreground">Map integration will show expanding search radius</p>
                  </div>
                )}

                {/* AI Assistant and Mock Donor Response (shown after SOS submission) */}
                {showMockDonors && (
                  <div className="space-y-6 mt-6">
                    <h2 className="text-xl font-bold text-destructive">🚨 Emergency Response System</h2>
                    <MockDonorResponse
                      requiredBloodType={sosFormData.bloodType || "B+"}
                      requiredComponent={sosFormData.bloodComponent || "Single Donor Platelet"}
                      onContactDonor={handleContactDonor}
                    />
                  </div>
                )}
                
                {donorsFound.length > 0 && (
                  <div className="space-y-4 mt-4">
                    <h3 className="text-lg font-semibold text-primary">Donors Found ({donorsFound.length})</h3>
                    {donorsFound.map((donor, index) => (
                      <div key={index} className="p-4 bg-background/50 rounded-lg border border-primary/20">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-semibold">{donor.name}</h4>
                            <p className="text-sm text-muted-foreground">📍 {donor.area} • {donor.distance}</p>
                            <p className="text-sm text-muted-foreground mt-1">📞 {donor.phone}</p>
                          </div>
                          <Badge className="bg-primary">{donor.bloodGroup}</Badge>
                        </div>
                        <Button 
                          size="sm" 
                          className="w-full bg-primary hover:bg-primary/90"
                          onClick={() => {
                            setScheduledDonations([...scheduledDonations, {
                              donor: donor.name,
                              area: donor.area,
                              date: new Date().toISOString().split('T')[0],
                              status: 'confirmed'
                            }]);
                          }}
                        >
                          Request Donation
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="future" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader><CardTitle>Scheduled Donations</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {scheduledDonations.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">No scheduled donations</p>
                ) : (
                  scheduledDonations.map((donation, index) => (
                    <div key={index} className="p-4 bg-background/50 rounded-lg border border-primary/10">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold">{donation.donor}</h4>
                          <p className="text-sm text-muted-foreground">📍 {donation.area}</p>
                          <p className="text-sm text-muted-foreground mt-1">📅 {donation.date}</p>
                        </div>
                        <Badge className="bg-primary">{donation.status}</Badge>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="health" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader><CardTitle>Health Analytics</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-background/50 rounded-lg">
                    <div className="text-2xl font-bold">130/85</div>
                    <div className="text-sm text-muted-foreground">Blood Pressure</div>
                    <Badge className="mt-2 bg-destructive">High</Badge>
                  </div>
                  <div className="text-center p-4 bg-background/50 rounded-lg">
                    <div className="text-2xl font-bold">110</div>
                    <div className="text-sm text-muted-foreground">Sugar (mg/dL)</div>
                    <Badge className="mt-2 bg-primary">Normal</Badge>
                  </div>
                  <div className="text-center p-4 bg-background/50 rounded-lg">
                    <div className="text-2xl font-bold">11.2</div>
                    <div className="text-sm text-muted-foreground">Hemoglobin (g/dL)</div>
                    <Badge className="mt-2 bg-destructive">Low</Badge>
                  </div>
                  <div className="text-center p-4 bg-background/50 rounded-lg">
                    <div className="text-2xl font-bold">85</div>
                    <div className="text-sm text-muted-foreground">Heart Rate (bpm)</div>
                    <Badge className="mt-2 bg-primary">Normal</Badge>
                  </div>
                  <div className="text-center p-4 bg-background/50 rounded-lg">
                    <div className="text-2xl font-bold">98.6°F</div>
                    <div className="text-sm text-muted-foreground">Temperature</div>
                    <Badge className="mt-2 bg-primary">Normal</Badge>
                  </div>
                  <div className="text-center p-4 bg-background/50 rounded-lg">
                    <div className="text-2xl font-bold">95%</div>
                    <div className="text-sm text-muted-foreground">Oxygen Level</div>
                    <Badge className="mt-2 bg-primary">Normal</Badge>
                  </div>
                </div>
                <div className="mt-6 p-4 bg-primary/10 rounded-lg">
                  <h4 className="font-semibold mb-2">Recent Transfusions</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Last Transfusion:</span>
                      <span>15 days ago</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Units:</span>
                      <span>8 units</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="chat" className="animate-fade-in">
            <AIChat 
              userType="patient" 
              userId={localStorage.getItem('userId') || ''} 
              className="h-full"
            />
          </TabsContent>
            </Tabs>
          </div>

          {/* Right Sidebar - Patient Profile Only */}
          <div className="lg:col-span-1 space-y-6">
            {/* Patient Profile */}
            <PatientProfile />
          </div>
        </div>
      </div>
      
      <VoiceAssistant />
    </div>
  );
};
