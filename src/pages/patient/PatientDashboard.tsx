import { useState } from 'react';
import { Heart, AlertTriangle, Calendar, Activity, MessageCircle, LogOut, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BloodCells } from '@/components/BloodCells';
import { LanguageSelector } from '@/components/LanguageSelector';
import { useLanguage } from '@/contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';

export const PatientDashboard = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('sos');
  const [searching, setSearching] = useState(false);

  const handleSOS = () => {
    setSearching(true);
    setTimeout(() => setSearching(false), 3000);
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
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="future" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader><CardTitle>Schedule Future Donation</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <Input type="date" className="bg-background/50 border-primary/20" />
                <Button className="w-full bg-primary hover:bg-primary/90">Schedule Request</Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="health" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader><CardTitle>Health Records</CardTitle></CardHeader>
              <CardContent><p className="text-muted-foreground">Track medications, transfusion history, and health data</p></CardContent>
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
    </div>
  );
};
