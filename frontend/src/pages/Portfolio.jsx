import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { Hero } from '../components/Hero';
import { ProjectCard } from '../components/ProjectCard';
import { Footer } from '../components/Footer';
import { NeuralNetworkLayer } from '../components/NeuralNetworkLayer';
import { githubAPI } from '../services/api';
import { roadmapPhases, techStack, achievements } from '../mock';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Skeleton } from '../components/ui/skeleton';
import { Target, Rocket, Lightbulb, Code2, Database, Cloud, Cpu, Award, CheckCircle2, Circle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

export const Portfolio = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [userData, setUserData] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data on mount
  useEffect(() => {
    fetchAllData();
  }, []);

  // Fetch repositories when category changes
  useEffect(() => {
    if (!loading) {
      fetchRepositories(selectedCategory);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategory]);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch user data, repositories, and stats in parallel
      const [userResponse, reposResponse, statsResponse] = await Promise.all([
        githubAPI.getUser(),
        githubAPI.getRepositories(),
        githubAPI.getStats()
      ]);

      if (userResponse.success) {
        setUserData(userResponse.data);
      }
      
      if (reposResponse.success) {
        setRepositories(reposResponse.data);
      }
      
      if (statsResponse.success) {
        setStats(statsResponse.data);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load GitHub data. Please try again later.');
      setLoading(false);
      toast.error('Failed to load GitHub data', {
        description: 'Using cached data if available'
      });
    }
  };

  const fetchRepositories = async (category) => {
    try {
      const response = await githubAPI.getRepositories(category === 'all' ? null : category);
      if (response.success) {
        setRepositories(response.data);
      }
    } catch (err) {
      console.error('Error fetching repositories:', err);
      toast.error('Failed to filter projects');
    }
  };

  const categories = [
    { value: 'all', label: 'All Projects' },
    { value: 'core', label: 'Core Projects' },
    { value: 'tools', label: 'Tools' },
    { value: 'research', label: 'Research' },
    { value: 'backend', label: 'Backend' },
    { value: 'resources', label: 'Resources' }
  ];

  // Featured project (first core project)
  const featuredProject = repositories.find(repo => repo.category === 'core') || repositories[0];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Header />
      <Hero userData={userData} stats={stats} loading={loading} />
      <NeuralNetworkLayer />

      {/* About Section */}
      <section id="about" className="py-24 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              About Me
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
              I build <span className="text-cyan-500 font-semibold">AI-powered systems, not just apps</span>. My mission is to create intelligent, 
              scalable automation frameworks that bridge the gap between traditional software and artificial intelligence.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Focus Areas */}
            <Card className="border-slate-200 dark:border-slate-800 bg-gradient-to-br from-cyan-50 to-white dark:from-slate-800 dark:to-slate-900">
              <CardHeader>
                <Rocket className="w-10 h-10 text-cyan-500 mb-2" />
                <CardTitle className="text-lg">AI-Powered Automation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Building systems that think and act intelligently
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 dark:border-slate-800 bg-gradient-to-br from-teal-50 to-white dark:from-slate-800 dark:to-slate-900">
              <CardHeader>
                <Code2 className="w-10 h-10 text-teal-500 mb-2" />
                <CardTitle className="text-lg">Robust API Architecture</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Designing scalable, maintainable APIs
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 dark:border-slate-800 bg-gradient-to-br from-cyan-50 to-white dark:from-slate-800 dark:to-slate-900">
              <CardHeader>
                <Cpu className="w-10 h-10 text-cyan-500 mb-2" />
                <CardTitle className="text-lg">Intelligent Systems</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Creating adaptive, learning-capable applications
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 dark:border-slate-800 bg-gradient-to-br from-teal-50 to-white dark:from-slate-800 dark:to-slate-900">
              <CardHeader>
                <Database className="w-10 h-10 text-teal-500 mb-2" />
                <CardTitle className="text-lg">System Software</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Deep dive into core infrastructure and automation
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Philosophy */}
          <div className="mt-16 text-center">
            <div className="inline-block px-8 py-4 bg-gradient-to-r from-cyan-50 to-teal-50 dark:from-slate-800 dark:to-slate-800 rounded-2xl border border-cyan-200 dark:border-cyan-900">
              <Lightbulb className="w-8 h-8 text-cyan-500 mx-auto mb-2" />
              <p className="text-xl font-semibold text-slate-900 dark:text-white italic">
                "Build in public, fail in public, learn in public"
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Main Project Highlight */}
      {featuredProject && (
        <section className="py-24 bg-slate-50 dark:bg-slate-950">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <Badge className="mb-4 bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400 border-0">
                Featured Project
              </Badge>
              <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
                {featuredProject.name}
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400">
                {featuredProject.description}
              </p>
            </div>

            <Card className="border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
              <CardContent className="p-8 md:p-12">
                <div className="grid md:grid-cols-2 gap-12">
                  <div>
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                      Project Vision
                    </h3>
                    <p className="text-slate-600 dark:text-slate-400 mb-6">
                      Transforming from a static portfolio → AI-Powered Agent System
                    </p>

                    <h4 className="text-xl font-semibold text-slate-900 dark:text-white mb-4 mt-8">
                      Repository Stats
                    </h4>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-cyan-50 dark:bg-slate-800 rounded-lg">
                        <div className="text-2xl font-bold text-cyan-500">{featuredProject.stars}</div>
                        <div className="text-xs text-slate-600 dark:text-slate-400">Stars</div>
                      </div>
                      <div className="text-center p-4 bg-teal-50 dark:bg-slate-800 rounded-lg">
                        <div className="text-2xl font-bold text-teal-500">{featuredProject.forks}</div>
                        <div className="text-xs text-slate-600 dark:text-slate-400">Forks</div>
                      </div>
                      <div className="text-center p-4 bg-cyan-50 dark:bg-slate-800 rounded-lg">
                        <div className="text-2xl font-bold text-cyan-500">{featuredProject.status}</div>
                        <div className="text-xs text-slate-600 dark:text-slate-400">Status</div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                      Technologies
                    </h3>
                    <div className="flex flex-wrap gap-2 mb-6">
                      {featuredProject.tags && featuredProject.tags.map((tag, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className="border-cyan-200 dark:border-cyan-900 text-cyan-700 dark:text-cyan-400"
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    <div className="mt-8">
                      <Button
                        className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white"
                        asChild
                      >
                        <a href={featuredProject.url} target="_blank" rel="noopener noreferrer">
                          View on GitHub
                        </a>
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      {/* Projects Section */}
      <section id="projects" className="py-24 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Core Projects Ecosystem
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Explore my portfolio of AI-powered systems and automation tools
            </p>
          </div>

          {/* Filter Buttons */}
          <div className="flex flex-wrap justify-center gap-2 mb-12">
            {categories.map((category) => (
              <Button
                key={category.value}
                variant={selectedCategory === category.value ? 'default' : 'outline'}
                onClick={() => setSelectedCategory(category.value)}
                className={
                  selectedCategory === category.value
                    ? 'bg-gradient-to-r from-cyan-500 to-teal-500 text-white'
                    : 'border-slate-300 dark:border-slate-700 hover:border-cyan-500'
                }
              >
                {category.label}
              </Button>
            ))}
          </div>

          {/* Error State */}
          {error && (
            <div className="flex items-center justify-center gap-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900 rounded-lg mb-8">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="border-slate-200 dark:border-slate-800">
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-2/3" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-20 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            /* Projects Grid */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {repositories.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          )}

          {repositories.length === 0 && !loading && (
            <div className="text-center py-12">
              <p className="text-slate-600 dark:text-slate-400">
                No projects found in this category.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Roadmap Section */}
      <section id="roadmap" className="py-24 bg-slate-50 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Development Roadmap
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              The journey from foundation to AI-powered optimization
            </p>
          </div>

          <div className="space-y-8">
            {roadmapPhases.map((phase, index) => (
              <Card
                key={phase.phase}
                className={`border-2 ${
                  phase.status === 'active'
                    ? 'border-cyan-500 dark:border-cyan-500'
                    : 'border-slate-200 dark:border-slate-800'
                } bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm`}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div
                        className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl ${
                          phase.status === 'active'
                            ? 'bg-gradient-to-r from-cyan-500 to-teal-500 text-white'
                            : phase.status === 'upcoming'
                            ? 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                            : 'bg-slate-100 dark:bg-slate-900 text-slate-400'
                        }`}
                      >
                        {phase.phase}
                      </div>
                      <div>
                        <CardTitle className="text-2xl">{phase.title}</CardTitle>
                        <CardDescription>{phase.period}</CardDescription>
                      </div>
                    </div>
                    <Badge
                      className={`${
                        phase.status === 'active'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : phase.status === 'upcoming'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                          : 'bg-slate-100 text-slate-800 dark:bg-slate-900/30 dark:text-slate-400'
                      } border-0`}
                    >
                      {phase.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-slate-600 dark:text-slate-400">Overall Progress</span>
                      <span className="font-semibold text-cyan-500">{phase.progress}%</span>
                    </div>
                    <Progress value={phase.progress} className="h-2" />
                  </div>
                  <div className="grid md:grid-cols-2 gap-3">
                    {phase.items.map((item, itemIndex) => (
                      <div
                        key={itemIndex}
                        className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50"
                      >
                        {item.completed ? (
                          <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                        ) : (
                          <Circle className="w-5 h-5 text-slate-400 flex-shrink-0" />
                        )}
                        <span
                          className={`text-sm ${
                            item.completed
                              ? 'text-slate-900 dark:text-white'
                              : 'text-slate-600 dark:text-slate-400'
                          }`}
                        >
                          {item.name}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section id="tech" className="py-24 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Technology Stack
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Tools and technologies I use to build intelligent systems
            </p>
          </div>

          <Tabs defaultValue="frontend" className="w-full">
            <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6 mb-8">
              <TabsTrigger value="frontend">Frontend</TabsTrigger>
              <TabsTrigger value="backend">Backend</TabsTrigger>
              <TabsTrigger value="ai">AI/ML</TabsTrigger>
              <TabsTrigger value="databases">Databases</TabsTrigger>
              <TabsTrigger value="devops">DevOps</TabsTrigger>
              <TabsTrigger value="infrastructure">Infrastructure</TabsTrigger>
            </TabsList>

            {Object.entries(techStack).map(([key, technologies]) => (
              <TabsContent key={key} value={key}>
                <Card className="border-slate-200 dark:border-slate-800">
                  <CardContent className="pt-6">
                    <div className="flex flex-wrap gap-3">
                      {technologies.map((tech, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className="px-4 py-2 text-base border-2 border-cyan-200 dark:border-cyan-900 bg-cyan-50 dark:bg-cyan-900/20 text-cyan-700 dark:text-cyan-400 hover:bg-cyan-100 dark:hover:bg-cyan-900/30 transition-colors"
                        >
                          {tech}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </section>

      {/* Achievements Section */}
      <section className="py-24 bg-slate-50 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Award className="w-16 h-16 text-cyan-500 mx-auto mb-4" />
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Key Achievements
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Milestones in my development journey
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {achievements.map((achievement, index) => (
              <Card
                key={index}
                className="border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm"
              >
                <CardHeader>
                  <CardTitle className="text-xl text-cyan-500">{achievement.category}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {achievement.items.map((item, itemIndex) => (
                      <li key={itemIndex} className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-teal-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-24 bg-white dark:bg-slate-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
            Let's Connect!
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 mb-8">
            I'm always excited to discuss AI/ML integration strategies, system architecture, and collaboration opportunities.
          </p>

          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <Card className="border-slate-200 dark:border-slate-800 bg-gradient-to-br from-cyan-50 to-white dark:from-slate-800 dark:to-slate-900">
              <CardHeader>
                <Target className="w-10 h-10 text-cyan-500 mx-auto mb-2" />
                <CardTitle>Interested In</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400 text-left">
                  <li>💬 AI/ML integration strategies</li>
                  <li>🏗️ System architecture and design patterns</li>
                  <li>🤝 Collaboration opportunities</li>
                  <li>📚 Knowledge sharing and mentoring</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-slate-200 dark:border-slate-800 bg-gradient-to-br from-teal-50 to-white dark:from-slate-800 dark:to-slate-900">
              <CardHeader>
                <Rocket className="w-10 h-10 text-teal-500 mx-auto mb-2" />
                <CardTitle>Get In Touch</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <a
                    href="mailto:amirulhafiz1132002@gmail.com"
                    className="block text-cyan-500 hover:text-cyan-600 transition-colors"
                  >
                    amirulhafiz1132002@gmail.com
                  </a>
                  {userData && (
                    <a
                      href={userData.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block text-cyan-500 hover:text-cyan-600 transition-colors"
                    >
                      @{userData.username}
                    </a>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="p-8 bg-gradient-to-r from-cyan-50 via-teal-50 to-cyan-50 dark:from-slate-800 dark:via-slate-800 dark:to-slate-800 rounded-2xl border border-cyan-200 dark:border-cyan-900">
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
              Let's build something amazing together!
            </h3>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              Explore my repositories, follow the development journey, and feel free to contribute or collaborate.
            </p>
            <Button
              size="lg"
              className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white shadow-lg hover:shadow-xl transition-all"
              asChild
            >
              <a href="https://github.com/amirulhafiz1132002-code" target="_blank" rel="noopener noreferrer">
                View GitHub Profile
              </a>
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};
