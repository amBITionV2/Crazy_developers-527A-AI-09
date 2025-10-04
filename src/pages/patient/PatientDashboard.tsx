import { useState } from 'react';
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
import { useLanguage } from '@/contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';

export const PatientDashboard = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('sos');
  const [searching, setSearching] = useState(false);
  const [donorsFound, setDonorsFound] = useState<any[]>([]);
  const [scheduledDonations, setScheduledDonations] = useState<any[]>([]);

  const handleSOS = () => {
    setSearching(true);
    setTimeout(() => {
      setSearching(false);
      setDonorsFound([
        { name: 'Rajesh Kumar', distance: '1.2 km', area: 'Jayanagar', bloodGroup: 'O+', phone: '+91 98765 43210' },
        { name: 'Priya Sharma', distance: '2.8 km', area: 'Koramangala', bloodGroup: 'O+', phone: '+91 98765 43211' },
        { name: 'Amit Patel', distance: '4.5 km', area: 'BTM Layout', bloodGroup: 'O+', phone: '+91 98765 43212' },
      ]);
    }, 3000);
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
            <LanguageSelector />
            <Button variant="outline" size="sm" onClick={() => navigate('/')} className="border-primary/20">
              <LogOut className="w-4 h-4 mr-2" />Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="relative z-10 container mx-auto px-4 py-8">
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
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Patient Name</Label>
                    <Input placeholder="Enter patient name" className="bg-background/50 border-primary/20" />
                  </div>
                  <div className="space-y-2">
                    <Label>Hospital</Label>
                    <Input placeholder="Hospital name" className="bg-background/50 border-primary/20" />
                  </div>
                  <div className="space-y-2">
                    <Label>Blood Type</Label>
                    <Select><SelectTrigger className="bg-background/50 border-primary/20"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent><SelectItem value="o+">O+</SelectItem><SelectItem value="a+">A+</SelectItem></SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Urgency Level</Label>
                    <Select><SelectTrigger className="bg-background/50 border-primary/20"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent><SelectItem value="critical">Critical</SelectItem><SelectItem value="high">High</SelectItem></SelectContent>
                    </Select>
                  </div>
                </div>
                <Button onClick={handleSOS} className="w-full bg-destructive hover:bg-destructive/90 text-white py-6 text-lg animate-pulse-glow">
                  <AlertTriangle className="w-5 h-5 mr-2" />Send SOS Alert
                </Button>
                {searching && (
                  <div className="p-6 bg-primary/10 rounded-lg text-center space-y-4">
                    <MapPin className="w-12 h-12 mx-auto text-primary animate-pulse" />
                    <p className="text-lg font-semibold">Searching for donors within 1-5 km radius...</p>
                    <p className="text-sm text-muted-foreground">Map integration will show expanding search radius</p>
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
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader><CardTitle>AI Prediction & Chat</CardTitle></CardHeader>
              <CardContent><p className="text-muted-foreground">Predict blood availability using AI/ML with multilingual voice support</p></CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      
      <VoiceAssistant />
    </div>
  );
};
