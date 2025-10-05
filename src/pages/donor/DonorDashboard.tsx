import { useState, useEffect } from 'react';
import { Heart, Activity, History, Calendar, AlertCircle, MessageCircle, Users, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { BloodCells } from '@/components/BloodCells';
import { LanguageSelector } from '@/components/LanguageSelector';
import { VoiceAssistant } from '@/components/VoiceAssistant';
import { AIChat } from '@/components/AIChat';
import { useLanguage } from '@/contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';
import { emergencyAPI, healthAPI, donationsAPI } from '@/lib/api';
import { toast } from 'sonner';
import { useWebSocket, WebSocketMessage, EmergencyAlert as WSEmergencyAlert } from '@/services/websocketService';

export const DonorDashboard = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const websocket = useWebSocket();
  const [activeTab, setActiveTab] = useState('health');
  const [scheduledRequests, setScheduledRequests] = useState([]);
  const [emergencyRequests, setEmergencyRequests] = useState([]);
  const [healthData, setHealthData] = useState(null);
  const [donationHistory, setDonationHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const userId = localStorage.getItem('userId');
        const authToken = localStorage.getItem('authToken');
        
        // Check if user is authenticated
        if (!userId || !authToken) {
          navigate('/select-user');
          return;
        }

        // Connect to WebSocket for real-time notifications
        websocket.connect(userId);

        // Load all dashboard data
        const [emergencyRes, healthRes, donationsRes] = await Promise.all([
          emergencyAPI.getEmergencyAlerts(),
          healthAPI.getHealthScore(userId),
          donationsAPI.getHistory(userId),
        ]);

        setEmergencyRequests(emergencyRes.success ? emergencyRes.alerts : []);
        setHealthData(healthRes);
        setDonationHistory(donationsRes);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    // WebSocket message handler
    const handleWebSocketMessage = (message: WebSocketMessage) => {
      console.log('📨 Received WebSocket message:', message);
      
      if (message.type === 'emergency_alert') {
        const alertData = message.data as WSEmergencyAlert;
        
        // Add to emergency requests
        const newAlert = {
          id: alertData.id,
          patient: alertData.patient_name,
          hospital: alertData.hospital_name,
          bloodGroup: alertData.blood_group,
          urgency: alertData.urgency_level,
          distance: 'Calculating...',
          area: 'Location pending',
          created_at: alertData.created_at
        };
        
        setEmergencyRequests(prev => [newAlert, ...prev]);
        
        // Show notification
        toast.error(`🚨 Emergency Alert: ${alertData.patient_name} needs ${alertData.blood_group} blood at ${alertData.hospital_name}`, {
          duration: 10000,
          action: {
            label: 'View',
            onClick: () => setActiveTab('emergency')
          }
        });
        
        // Play notification sound (optional)
        try {
          const audio = new Audio('/notification.mp3');
          audio.play().catch(() => console.log('Could not play notification sound'));
        } catch (e) {
          console.log('Audio notification not available');
        }
        
      } else if (message.type === 'connection_status') {
        const statusData = message.data as Record<string, unknown>;
        setWsConnected(statusData.status === 'connected');
      }
    };

    websocket.addMessageHandler(handleWebSocketMessage);
    loadDashboardData();

    // Cleanup on unmount
    return () => {
      websocket.removeMessageHandler(handleWebSocketMessage);
    };
  }, [navigate, websocket]);

  const healthScore = healthData?.overall_score || 85;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <BloodCells />
      
      {/* Header */}
      <header className="relative z-10 bg-card/30 backdrop-blur-sm border-b border-primary/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center">
              <Heart className="w-5 h-5 text-white fill-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-primary">{t('appName')}</h1>
              <p className="text-sm text-muted-foreground">{t('donor')} {t('dashboard')}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-xs text-muted-foreground">
                {wsConnected ? 'Real-time alerts active' : 'Connecting...'}
              </span>
            </div>
            <LanguageSelector />
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                // Clear authentication data
                localStorage.removeItem('authToken');
                localStorage.removeItem('user');
                localStorage.removeItem('userId');
                navigate('/');
              }}
              className="border-primary/20 hover:bg-primary/10"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Dashboard Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-card/50 backdrop-blur-sm border border-primary/20 p-1 grid grid-cols-3 lg:grid-cols-6 gap-2">
            <TabsTrigger value="health" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <Activity className="w-4 h-4 mr-2" />
              {t('healthStatus')}
            </TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <History className="w-4 h-4 mr-2" />
              {t('history')}
            </TabsTrigger>
            <TabsTrigger value="schedule" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <Calendar className="w-4 h-4 mr-2" />
              {t('schedule')}
            </TabsTrigger>
            <TabsTrigger value="emergency" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <AlertCircle className="w-4 h-4 mr-2" />
              {t('emergency')}
            </TabsTrigger>
            <TabsTrigger value="chat" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <MessageCircle className="w-4 h-4 mr-2" />
              AI Chat
            </TabsTrigger>
            <TabsTrigger value="community" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <Users className="w-4 h-4 mr-2" />
              {t('community')}
            </TabsTrigger>
          </TabsList>

          {/* Health Status Tab */}
          <TabsContent value="health" className="space-y-6 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle>Health Score</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="text-5xl font-bold text-primary mb-2">{healthScore}%</div>
                    <Progress value={healthScore} className="h-3" />
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">118/78</div>
                      <div className="text-sm text-muted-foreground">Blood Pressure</div>
                      <Badge className="mt-2 bg-green-100 text-green-800">Optimal</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">15.2</div>
                      <div className="text-sm text-muted-foreground">Hemoglobin (g/dL)</div>
                      <Badge className="mt-2 bg-green-100 text-green-800">Excellent</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">92</div>
                      <div className="text-sm text-muted-foreground">Blood Sugar (mg/dL)</div>
                      <Badge className="mt-2 bg-green-100 text-green-800">Normal</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">68</div>
                      <div className="text-sm text-muted-foreground">Resting HR (bpm)</div>
                      <Badge className="mt-2 bg-green-100 text-green-800">Athletic</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">72</div>
                      <div className="text-sm text-muted-foreground">Weight (kg)</div>
                      <Badge className="mt-2 bg-green-100 text-green-800">Ideal</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">98%</div>
                      <div className="text-sm text-muted-foreground">Blood Oxygen</div>
                      <Badge className="mt-2 bg-green-100 text-green-800">Perfect</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle>Donation Eligibility & Profile</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                    <span className="font-medium">Current Status</span>
                    <Badge className="bg-green-100 text-green-800 border-green-300">✅ Eligible to Donate</Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Blood Group</span>
                        <span className="font-medium text-primary">O+ (Universal Donor)</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Last Donation</span>
                        <span className="font-medium">Sept 15, 2024 (50 days ago)</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Next Eligible</span>
                        <span className="font-medium text-green-600">Now Available</span>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Total Donations</span>
                        <span className="font-semibold text-primary">12 donations</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Lives Impacted</span>
                        <span className="font-semibold text-green-600">36 people</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Donor Since</span>
                        <span className="font-medium">July 2022</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-primary/10">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium">Donation Progress</span>
                      <span className="text-sm text-muted-foreground">12/20 goal</span>
                    </div>
                    <Progress value={60} className="h-2" />
                    <p className="text-xs text-muted-foreground mt-2">8 more donations to reach your annual goal!</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader>
                <CardTitle>Donation History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { patient: 'Rajesh Kumar', hospital: 'Fortis Hospital, Bangalore', bloodGroup: 'O+', date: '2024-09-15', status: 'Completed', units: 450, impact: 'Helped 3 patients' },
                    { patient: 'Priya Sharma', hospital: 'Manipal Hospital, Bangalore', bloodGroup: 'O+', date: '2024-07-20', status: 'Completed', units: 450, impact: 'Emergency surgery success' },
                    { patient: 'Arun Reddy', hospital: 'Apollo Hospital, Bangalore', bloodGroup: 'O+', date: '2024-05-10', status: 'Completed', units: 450, impact: 'Cancer patient support' },
                    { patient: 'Meera Patel', hospital: 'Narayana Health, Bangalore', bloodGroup: 'O+', date: '2024-03-05', status: 'Completed', units: 450, impact: 'Accident victim recovery' },
                    { patient: 'Kiran Singh', hospital: 'NIMHANS, Bangalore', bloodGroup: 'O+', date: '2024-01-12', status: 'Completed', units: 450, impact: 'Critical patient saved' },
                  ].map((donation, index) => (
                    <div key={index} className="p-4 bg-background/50 rounded-lg border border-primary/10 hover:border-primary/30 transition-colors">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h4 className="font-semibold text-primary">{donation.patient}</h4>
                          <p className="text-sm text-muted-foreground">{donation.hospital}</p>
                          <p className="text-sm text-green-600 mt-1">✨ {donation.impact}</p>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline" className="border-primary text-primary mb-1">{donation.bloodGroup}</Badge>
                          <div className="text-xs text-muted-foreground">{donation.units}ml</div>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <p className="text-sm text-muted-foreground">{donation.date}</p>
                        <Badge className="bg-green-100 text-green-800 border-green-200">{donation.status}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Donation Stats Summary */}
                <div className="mt-6 p-4 bg-primary/5 rounded-lg border border-primary/20">
                  <h4 className="font-semibold text-primary mb-3">Your Impact</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">12</div>
                      <div className="text-sm text-muted-foreground">Total Donations</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">36</div>
                      <div className="text-sm text-muted-foreground">Lives Saved</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">5.4L</div>
                      <div className="text-sm text-muted-foreground">Blood Donated</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">2.5</div>
                      <div className="text-sm text-muted-foreground">Years Active</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Schedule Tab */}
          <TabsContent value="schedule" className="animate-fade-in">
            <div className="space-y-6">
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    📅 Upcoming Donation Appointments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      {
                        id: 1,
                        patient: 'Kiran Sharma (Cancer Patient)',
                        hospital: 'Tata Memorial Hospital, Bangalore',
                        date: '2024-10-08',
                        time: '10:30 AM',
                        bloodGroup: 'O+',
                        status: 'confirmed',
                        urgency: 'high',
                        contact: '+91-9876543210',
                        notes: 'Pre-surgery requirement for chemotherapy patient'
                      },
                      {
                        id: 2,
                        patient: 'Emergency Pool Donation',
                        hospital: 'Red Cross Blood Bank, Bangalore',
                        date: '2024-10-12',
                        time: '2:00 PM',
                        bloodGroup: 'O+',
                        status: 'pending',
                        urgency: 'medium',
                        contact: '+91-9876543211',
                        notes: 'Monthly voluntary donation for emergency reserves'
                      }
                    ].map((schedule) => (
                      <div key={schedule.id} className="p-4 bg-background/50 rounded-lg border border-primary/10 hover:border-primary/30 transition-all">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <h4 className="font-semibold text-primary">{schedule.patient}</h4>
                            <p className="text-sm text-muted-foreground">{schedule.hospital}</p>
                            <p className="text-sm mt-1">📅 {schedule.date} at {schedule.time}</p>
                            <p className="text-sm mt-1">📞 {schedule.contact}</p>
                            <p className="text-xs text-muted-foreground mt-2 italic">{schedule.notes}</p>
                          </div>
                          <div className="text-right space-y-1">
                            <Badge variant="outline" className="border-primary text-primary">{schedule.bloodGroup}</Badge>
                            <Badge className={`block ${
                              schedule.urgency === 'high' ? 'bg-red-100 text-red-800' :
                              schedule.urgency === 'medium' ? 'bg-orange-100 text-orange-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {schedule.urgency.toUpperCase()}
                            </Badge>
                          </div>
                        </div>
                        
                        {schedule.status === 'pending' && (
                          <div className="flex gap-2 mt-4">
                            <Button 
                              size="sm" 
                              className="bg-primary hover:bg-primary/90 flex-1"
                              onClick={() => {
                                const updated = [...scheduledRequests];
                                const existingIndex = updated.findIndex(req => req.patient === schedule.patient);
                                if (existingIndex >= 0) {
                                  updated[existingIndex].status = 'accepted';
                                } else {
                                  updated.push({
                                    patient: schedule.patient,
                                    hospital: schedule.hospital,
                                    date: schedule.date,
                                    status: 'accepted'
                                  });
                                }
                                setScheduledRequests(updated);
                                toast.success(`✅ Confirmed appointment with ${schedule.patient}`);
                              }}
                            >
                              ✅ Confirm Appointment
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="border-primary/20"
                              onClick={() => {
                                toast.info(`📞 Requesting reschedule for ${schedule.patient}`);
                              }}
                            >
                              📅 Reschedule
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="border-destructive text-destructive hover:bg-destructive/5"
                              onClick={() => {
                                toast.error(`❌ Declined appointment with ${schedule.patient}`);
                              }}
                            >
                              ❌ Decline
                            </Button>
                          </div>
                        )}
                        
                        {schedule.status === 'confirmed' && (
                          <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                            <div className="flex items-center justify-between">
                              <Badge className="bg-green-100 text-green-800">✅ Confirmed</Badge>
                              <Button size="sm" variant="outline" className="text-xs h-6">
                                📍 Get Directions
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                    
                    {scheduledRequests.length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        <div className="text-4xl mb-4">📅</div>
                        <p>No additional scheduled donations</p>
                        <p className="text-sm mt-2">Emergency requests will appear here when accepted</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Donation Reminders */}
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    🔔 Donation Reminders & Tips
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <h5 className="font-medium text-blue-800">💧 Pre-Donation Tips</h5>
                      <p className="text-sm text-blue-600 mt-1">
                        Drink extra fluids 24-48 hours before donation. Eat iron-rich foods and get good sleep.
                      </p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <h5 className="font-medium text-green-800">✅ Eligibility Check</h5>
                      <p className="text-sm text-green-600 mt-1">
                        Your next donation is available now. You're in excellent health for donation.
                      </p>
                    </div>
                    <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                      <h5 className="font-medium text-orange-800">📱 Quick Actions</h5>
                      <div className="flex gap-2 mt-2">
                        <Button size="sm" variant="outline" className="text-xs">
                          📅 Schedule New Donation
                        </Button>
                        <Button size="sm" variant="outline" className="text-xs">
                          📍 Find Blood Banks
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Emergency Tab */}
          <TabsContent value="emergency" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader>
                <CardTitle className="text-destructive flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 animate-pulse" />
                  Emergency Blood Requests
                </CardTitle>
                <p className="text-sm text-muted-foreground">Real-time urgent blood requirements in Bangalore</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { 
                      patient: 'Road Accident Victim #1247', 
                      hospital: 'Fortis Hospital, Bannerghatta Road', 
                      bloodGroup: 'O+', 
                      distance: '2.8 km', 
                      urgency: 'CRITICAL', 
                      area: 'Bannerghatta Road',
                      time: '12 mins ago',
                      condition: 'Multiple trauma, urgent surgery',
                      contact: '9876543210'
                    },
                    { 
                      patient: 'Emergency Case #2891', 
                      hospital: 'Apollo Hospital, Jayanagar', 
                      bloodGroup: 'O+', 
                      distance: '5.2 km', 
                      urgency: 'HIGH', 
                      area: 'Jayanagar 4th Block',
                      time: '28 mins ago',
                      condition: 'Cancer patient, pre-surgery',
                      contact: '9876543211'
                    },
                    { 
                      patient: 'Maternity Emergency #3456', 
                      hospital: 'Manipal Hospital, HAL Airport Road', 
                      bloodGroup: 'O+', 
                      distance: '7.1 km', 
                      urgency: 'HIGH', 
                      area: 'HAL Airport Road',
                      time: '1 hour ago',
                      condition: 'Postpartum hemorrhage',
                      contact: '9876543212'
                    },
                  ].map((emergency, index) => (
                    <div key={index} className="p-4 bg-destructive/5 rounded-lg border border-destructive/20 hover:border-destructive/40 transition-all duration-200 animate-pulse-glow">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h4 className="font-semibold text-destructive flex items-center gap-2">
                            🚨 {emergency.patient}
                          </h4>
                          <p className="text-sm text-muted-foreground font-medium">{emergency.hospital}</p>
                          <p className="text-sm mt-1 text-blue-600">📍 {emergency.area} • {emergency.distance}</p>
                          <p className="text-sm mt-1 text-orange-600">⚕️ {emergency.condition}</p>
                          <p className="text-xs text-muted-foreground mt-1">📞 Contact: {emergency.contact}</p>
                        </div>
                        <div className="text-right space-y-1">
                          <Badge className="bg-destructive text-white">{emergency.bloodGroup}</Badge>
                          <Badge 
                            variant="outline" 
                            className={`block text-xs ${
                              emergency.urgency === 'CRITICAL' 
                                ? 'border-red-500 text-red-600 bg-red-50' 
                                : 'border-orange-500 text-orange-600 bg-orange-50'
                            }`}
                          >
                            {emergency.urgency}
                          </Badge>
                          <div className="text-xs text-muted-foreground">{emergency.time}</div>
                        </div>
                      </div>
                      <div className="flex gap-2 mt-4">
                        <Button 
                          size="sm" 
                          className="bg-destructive hover:bg-destructive/90 text-white flex-1"
                          onClick={() => {
                            toast.success(`✅ Accepted emergency request for ${emergency.patient}`);
                            setScheduledRequests([...scheduledRequests, {
                              patient: emergency.patient,
                              hospital: emergency.hospital,
                              date: new Date().toISOString().split('T')[0],
                              status: 'accepted'
                            }]);
                          }}
                        >
                          🩸 Accept & Donate
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="border-destructive/20 hover:bg-destructive/5"
                          onClick={() => toast.info(`Declined request for ${emergency.patient}`)}
                        >
                          ❌ Not Available
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {/* Quick Stats */}
                  <div className="mt-6 p-4 bg-destructive/5 rounded-lg border border-destructive/20">
                    <h4 className="font-semibold text-destructive mb-3">📊 Emergency Response Stats</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-xl font-bold text-destructive">8</div>
                        <div className="text-xs text-muted-foreground">Emergencies Helped</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-green-600">95%</div>
                        <div className="text-xs text-muted-foreground">Response Rate</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-600">12min</div>
                        <div className="text-xs text-muted-foreground">Avg Response Time</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-orange-600">3.2km</div>
                        <div className="text-xs text-muted-foreground">Avg Distance</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AI Chat Tab */}
          <TabsContent value="chat" className="animate-fade-in">
            <AIChat 
              userType="donor" 
              userId={localStorage.getItem('userId') || ''} 
              className="h-full"
            />
          </TabsContent>

          {/* Community Tab */}
          <TabsContent value="community" className="animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    🏆 Donation Leaderboard
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'Rajesh Kumar', donations: 28, rank: 1, bloodGroup: 'O+', streak: 24 },
                      { name: 'Priya Sharma', donations: 25, rank: 2, bloodGroup: 'AB+', streak: 18 },
                      { name: 'Arjun Reddy', donations: 22, rank: 3, bloodGroup: 'B+', streak: 15 },
                      { name: 'You (Test Donor)', donations: 12, rank: 5, bloodGroup: 'O+', streak: 8 },
                      { name: 'Sneha Patel', donations: 11, rank: 6, bloodGroup: 'A+', streak: 6 },
                    ].map((donor) => (
                      <div key={donor.rank} className={`flex items-center justify-between p-3 rounded-lg transition-colors ${
                        donor.name.includes('You') 
                          ? 'bg-primary/10 border border-primary/30' 
                          : 'bg-background/50 border border-primary/10'
                      }`}>
                        <div className="flex items-center gap-3">
                          <Badge className={`${
                            donor.rank === 1 ? 'bg-yellow-500' :
                            donor.rank === 2 ? 'bg-gray-400' :
                            donor.rank === 3 ? 'bg-orange-600' :
                            'bg-primary'
                          } text-white min-w-[24px]`}>
                            {donor.rank === 1 ? '🥇' : 
                             donor.rank === 2 ? '🥈' : 
                             donor.rank === 3 ? '🥉' : donor.rank}
                          </Badge>
                          <div>
                            <span className={`font-medium ${donor.name.includes('You') ? 'text-primary' : ''}`}>
                              {donor.name}
                            </span>
                            <div className="text-xs text-muted-foreground">
                              {donor.bloodGroup} • {donor.streak} month streak
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">{donor.donations}</div>
                          <div className="text-xs text-muted-foreground">donations</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    📍 Nearby Active Donors
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'Amit Patel', distance: '1.2 km', bloodGroup: 'O+', status: 'Available', lastDonation: '2 weeks ago' },
                      { name: 'Sneha Reddy', distance: '2.5 km', bloodGroup: 'O+', status: 'Available', lastDonation: '1 month ago' },
                      { name: 'Karthik Rao', distance: '3.8 km', bloodGroup: 'O+', status: 'Recently Donated', lastDonation: '5 days ago' },
                      { name: 'Meera Singh', distance: '4.1 km', bloodGroup: 'O+', status: 'Available', lastDonation: '3 weeks ago' },
                    ].map((donor, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-background/50 rounded-lg border border-primary/10 hover:border-primary/30 transition-colors">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <div className="font-semibold">{donor.name}</div>
                            <div className={`w-2 h-2 rounded-full ${
                              donor.status === 'Available' ? 'bg-green-500' : 'bg-orange-500'
                            }`}></div>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            📍 {donor.distance} • Last: {donor.lastDonation}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {donor.status}
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline" className="border-primary text-primary mb-1">{donor.bloodGroup}</Badge>
                          <Button size="sm" variant="outline" className="text-xs h-6">
                            💬 Connect
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              
              {/* Achievements & Badges */}
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    🏅 Your Achievements
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { title: 'First Donation', emoji: '🩸', earned: true, date: 'July 2022' },
                      { title: 'Life Saver', emoji: '💝', earned: true, date: 'Sept 2022' },
                      { title: '10 Donations', emoji: '🎯', earned: true, date: 'Jan 2024' },
                      { title: 'Emergency Hero', emoji: '🚨', earned: true, date: 'March 2024' },
                      { title: '15 Donations', emoji: '⭐', earned: false, date: 'In Progress' },
                      { title: 'Year Warrior', emoji: '🏆', earned: false, date: '3 more needed' },
                    ].map((achievement, index) => (
                      <div key={index} className={`p-3 rounded-lg border text-center ${
                        achievement.earned 
                          ? 'bg-green-50 border-green-200' 
                          : 'bg-gray-50 border-gray-200 opacity-60'
                      }`}>
                        <div className="text-2xl mb-1">{achievement.emoji}</div>
                        <div className="text-xs font-medium">{achievement.title}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {achievement.date}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    📱 Recent Community Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { user: 'Rajesh Kumar', action: 'donated blood', time: '2 hours ago', icon: '🩸' },
                      { user: 'Priya Sharma', action: 'helped emergency case', time: '5 hours ago', icon: '🚨' },
                      { user: 'Arjun Reddy', action: 'reached 20 donations', time: '1 day ago', icon: '🎯' },
                      { user: 'Community', action: 'blood camp organized', time: '2 days ago', icon: '🏕️' },
                    ].map((activity, index) => (
                      <div key={index} className="flex items-center gap-3 p-2 bg-background/30 rounded">
                        <div className="text-lg">{activity.icon}</div>
                        <div className="flex-1">
                          <div className="text-sm">
                            <span className="font-medium">{activity.user}</span> {activity.action}
                          </div>
                          <div className="text-xs text-muted-foreground">{activity.time}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
      
      <VoiceAssistant />
    </div>
  );
};
