import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { useChatStore } from '../store/chatStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Calendar, MapPin, Users, Sparkles } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export function Dashboard() {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const { loadChatHistory } = useChatStore();
  const navigate = useNavigate();

  // Load chat history on mount so sidebar shows sessions
  useEffect(() => {
    loadChatHistory();
  }, [loadChatHistory]);

  const sampleQueries = [
    {
      icon: Calendar,
      title: t('dashboard.sampleQuery1Title'),
      query: t('dashboard.sampleQuery1'),
      category: t('dashboard.categorySchedule')
    },
    {
      icon: MapPin,
      title: t('dashboard.sampleQuery2Title'),
      query: t('dashboard.sampleQuery2'),
      category: t('dashboard.categoryLocation')
    },
    {
      icon: Users,
      title: t('dashboard.sampleQuery3Title'),
      query: t('dashboard.sampleQuery3'),
      category: t('dashboard.categoryLevel')
    },
    {
      icon: Sparkles,
      title: t('dashboard.sampleQuery4Title'),
      query: t('dashboard.sampleQuery4'),
      category: t('dashboard.categoryTopics')
    }
  ];

  const handleQueryClick = (query: string) => {
    navigate('/app/chat', { state: { initialQuery: query } });
  };

  return (
    <div className="h-full overflow-auto bg-background">
      <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        {/* Welcome Section */}
        <section className="mb-6 sm:mb-8" aria-labelledby="welcome-heading">
          <div className="flex items-center gap-3 sm:gap-4 mb-3">
            <img 
              src="/dati-logo.png" 
              alt="Dati company logo" 
              className="h-10 w-10 sm:h-12 sm:w-12 object-contain bg-white p-1.5 rounded"
            />
            <div>
              <h1 id="welcome-heading" className="text-2xl sm:text-3xl md:text-4xl font-bold text-foreground">
                {t('dashboard.welcomeBack')}{user?.companyName ? `, ${user.companyName}` : ''}!
              </h1>
            </div>
          </div>
          <p className="text-muted-foreground text-base sm:text-lg ml-0 sm:ml-16">
            {t('dashboard.subtitle')}
          </p>
        </section>

        {/* Quick Start Guide */}
        <Card className="mb-6 sm:mb-8 shadow-md hover:shadow-lg transition-shadow" role="region" aria-labelledby="quick-start-title">
          <CardHeader>
            <CardTitle id="quick-start-title" className="flex items-center gap-2 text-lg sm:text-xl">
              <MessageSquare className="h-5 w-5 sm:h-6 sm:w-6 text-dati-accent-1" aria-hidden="true" />
              {t('dashboard.quickStartGuide')}
            </CardTitle>
            <CardDescription className="text-sm sm:text-base">
              {t('dashboard.quickStartDescription')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-sm sm:text-base text-gray-900 mb-2 sm:mb-3">{t('dashboard.whatCanYouAsk')}</h3>
                <ul className="space-y-2 text-sm sm:text-base text-gray-600" role="list">
                  <li className="flex items-start gap-2">
                    <span className="text-dati-accent-1 mt-0.5 flex-shrink-0" aria-hidden="true">•</span>
                    <span>{t('dashboard.findSessions')}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-dati-accent-1 mt-0.5 flex-shrink-0" aria-hidden="true">•</span>
                    <span>{t('dashboard.searchTopics')}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-dati-accent-1 mt-0.5 flex-shrink-0" aria-hidden="true">•</span>
                    <span>{t('dashboard.getRecommendations')}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-dati-accent-1 mt-0.5 flex-shrink-0" aria-hidden="true">•</span>
                    <span>{t('dashboard.buildSchedule')}</span>
                  </li>
                </ul>
              </div>
              <div className="pt-2">
                <Button 
                  onClick={() => navigate('/app/chat')}
                  className="bg-dati-primary hover:bg-dati-accent-4 text-white shadow-md hover:shadow-lg transition-all focus:ring-2 focus:ring-dati-primary focus:ring-offset-2 w-full sm:w-auto"
                  aria-label={t('dashboard.aria.navigateToChat')}
                >
                  <MessageSquare className="h-4 w-4 mr-2" aria-hidden="true" />
                  {t('dashboard.startChatting')}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sample Queries */}
        <section className="mb-6 sm:mb-8" aria-labelledby="sample-queries-heading">
          <h2 id="sample-queries-heading" className="text-lg sm:text-xl font-semibold text-foreground mb-3 sm:mb-4">{t('dashboard.sampleQueries')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4" role="list">
            {sampleQueries.map((sample, index) => {
              const Icon = sample.icon;
              return (
                <Card 
                  key={index}
                  className="cursor-pointer hover:shadow-lg transition-all border-2 hover:border-dati-secondary hover:scale-105 focus-within:ring-2 focus-within:ring-dati-primary focus-within:ring-offset-2"
                  onClick={() => handleQueryClick(sample.query)}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleQueryClick(sample.query);
                    }
                  }}
                  role="button"
                  aria-label={`Try sample query: ${sample.query}`}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                        <div className="p-2 bg-dati-accent-1/10 rounded-lg flex-shrink-0">
                          <Icon className="h-4 w-4 sm:h-5 sm:w-5 text-dati-accent-1" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <CardTitle className="text-sm sm:text-base truncate">{sample.title}</CardTitle>
                          <Badge variant="secondary" className="mt-1 text-xs">
                            {sample.category}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-xs sm:text-sm text-gray-600 italic line-clamp-2">"{sample.query}"</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>

        {/* Tips Section */}
        <Card className="shadow-md" role="region" aria-labelledby="tips-heading">
          <CardHeader>
            <CardTitle id="tips-heading" className="text-base sm:text-lg">{t('dashboard.proTips')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 sm:space-y-3 text-sm sm:text-base text-gray-600" role="list">
              <li className="flex items-start gap-2">
                <span className="text-dati-accent-2 font-bold flex-shrink-0" role="img" aria-label="Light bulb">💡</span>
                <span>{t('dashboard.tip1')}</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-dati-accent-2 font-bold flex-shrink-0" role="img" aria-label="Light bulb">💡</span>
                <span>{t('dashboard.tip2')}</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-dati-accent-2 font-bold flex-shrink-0" role="img" aria-label="Light bulb">💡</span>
                <span>{t('dashboard.tip3')}</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
