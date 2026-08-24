import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { jobsApi, interviewPrepApi } from '../api/client';
import PrepPackChecklist from '../components/PrepPackChecklist';
import {
  Briefcase,
  Plus,
  Sparkles,
  FileText,
  Building,
  MapPin,
  DollarSign,
  ChevronRight,
  CheckCircle2,
  X,
  Edit,
  Trash2,
} from 'lucide-react';

export const JobTrackerPage = () => {
  const { user } = useAuth();

  const [jobs, setJobs] = useState([]);
  const [resume, setResume] = useState(null);
  const [resumeContent, setResumeContent] = useState('');
  const [loading, setLoading] = useState(true);

  // Selected job for prep pack modal / drawer
  const [selectedJob, setSelectedJob] = useState(null);
  const [prepPack, setPrepPack] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [prepError, setPrepError] = useState('');

  // New Job Form State
  const [showAddModal, setShowAddModal] = useState(false);
  const [showResumeModal, setShowResumeModal] = useState(false);

  const [companyName, setCompanyName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [status, setStatus] = useState('Applied');
  const [location, setLocation] = useState('');
  const [salaryRange, setSalaryRange] = useState('');
  const [isSubmittingJob, setIsSubmittingJob] = useState(false);

  const loadData = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [jobsRes, resumeRes] = await Promise.allSettled([
        jobsApi.listJobs(user.id),
        interviewPrepApi.getResume(user.id),
      ]);

      if (jobsRes.status === 'fulfilled') setJobs(jobsRes.value);
      if (resumeRes.status === 'fulfilled') {
        setResume(resumeRes.value);
        setResumeContent(resumeRes.value.content);
      }
    } catch (err) {
      console.error('Error loading job tracker data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleCreateJob = async (e) => {
    e.preventDefault();
    if (!companyName || !jobTitle || !jobDescription) return;

    setIsSubmittingJob(true);
    try {
      await jobsApi.createJob(user.id, {
        company_name: companyName,
        job_title: jobTitle,
        job_description: jobDescription,
        status,
        location,
        salary_range: salaryRange,
      });

      setCompanyName('');
      setJobTitle('');
      setJobDescription('');
      setStatus('Applied');
      setLocation('');
      setSalaryRange('');
      setShowAddModal(false);
      loadData();
    } catch (err) {
      console.error('Error creating job application:', err);
    } finally {
      setIsSubmittingJob(false);
    }
  };

  const handleStatusChange = async (jobId, newStatus) => {
    try {
      await jobsApi.updateJob(user.id, jobId, { status: newStatus });
      loadData();
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob({ ...selectedJob, status: newStatus });
      }
    } catch (err) {
      console.error('Error updating job status:', err);
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job application?')) return;
    try {
      await jobsApi.deleteJob(user.id, jobId);
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob(null);
        setPrepPack(null);
      }
      loadData();
    } catch (err) {
      console.error('Error deleting job:', err);
    }
  };

  const handleSaveResume = async () => {
    try {
      const updated = await interviewPrepApi.saveResume(user.id, {
        title: 'Main Resume',
        content: resumeContent,
      });
      setResume(updated);
      setShowResumeModal(false);
    } catch (err) {
      console.error('Error saving resume:', err);
    }
  };

  const handleOpenPrepPack = async (job) => {
    setSelectedJob(job);
    setPrepError('');
    setPrepPack(null);

    // If job has existing prep pack, fetch it
    if (job.has_prep_pack) {
      try {
        const pack = await interviewPrepApi.getPrepPack(user.id, job.id);
        setPrepPack(pack);
      } catch (err) {
        console.error('Error fetching prep pack:', err);
      }
    }
  };

  const handleGeneratePrepPack = async (job) => {
    setSelectedJob(job);
    setIsGenerating(true);
    setPrepError('');
    try {
      const pack = await interviewPrepApi.generatePrepPack(user.id, job.id);
      setPrepPack(pack);
      loadData();
    } catch (err) {
      console.error('Error generating prep pack:', err);
      setPrepError(err.response?.data?.detail || 'Failed to generate prep pack.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleItemUpdate = async (itemId, updateData) => {
    if (!selectedJob) return;
    try {
      await interviewPrepApi.updateItem(user.id, itemId, updateData);
      const updatedPack = await interviewPrepApi.getPrepPack(user.id, selectedJob.id);
      setPrepPack(updatedPack);
    } catch (err) {
      console.error('Error updating checklist item:', err);
    }
  };

  const getStatusBadgeClass = (s) => {
    switch (s) {
      case 'Interview':
        return 'bg-amber-100 text-amber-900 border-amber-300 font-bold';
      case 'Offered':
        return 'bg-emerald-100 text-emerald-900 border-emerald-300 font-bold';
      case 'Rejected':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      default:
        return 'bg-blue-50 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Job Applications & Interview Prep</h1>
          <p className="text-sm text-slate-500">
            Track job applications and generate AI-tailored checkable prep packs for any interview.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowResumeModal(true)}
            className="flex items-center space-x-2 px-3.5 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <FileText className="w-4 h-4 text-indigo-600" />
            <span>Manage My Resume</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Application</span>
          </button>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Job Applications List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-900">Applications ({jobs.length})</h2>
            <span className="text-xs text-slate-400">
              {jobs.filter((j) => j.status === 'Interview').length} Interviewing
            </span>
          </div>

          {loading ? (
            <div className="text-xs text-slate-400 py-8 text-center bg-white border border-slate-200 rounded-xl">
              Loading applications...
            </div>
          ) : jobs.length > 0 ? (
            <div className="space-y-3">
              {jobs.map((job) => {
                const isInterview = job.status === 'Interview';
                const isSelected = selectedJob && selectedJob.id === job.id;

                return (
                  <div
                    key={job.id}
                    className={`bg-white border rounded-xl p-4 shadow-sm space-y-3 transition-all ${
                      isSelected ? 'ring-2 ring-indigo-500 border-indigo-500' : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <Building className="w-4 h-4 text-indigo-600 shrink-0" />
                          <h3 className="font-bold text-slate-900 text-sm">{job.company_name}</h3>
                        </div>
                        <p className="text-xs font-medium text-slate-600 mt-0.5">{job.job_title}</p>
                      </div>

                      {/* Status Selector Dropdown */}
                      <select
                        value={job.status}
                        onChange={(e) => handleStatusChange(job.id, e.target.value)}
                        className={`text-[11px] font-bold px-2 py-1 rounded border focus:outline-none cursor-pointer ${getStatusBadgeClass(
                          job.status
                        )}`}
                      >
                        <option value="Applied">Applied</option>
                        <option value="Interview">Interview 🔥</option>
                        <option value="Offered">Offered 🎉</option>
                        <option value="Rejected">Rejected</option>
                      </select>
                    </div>

                    {(job.location || job.salary_range) && (
                      <div className="flex items-center space-x-3 text-[11px] text-slate-500">
                        {job.location && (
                          <span className="flex items-center">
                            <MapPin className="w-3 h-3 mr-1 text-slate-400" /> {job.location}
                          </span>
                        )}
                        {job.salary_range && (
                          <span className="flex items-center">
                            <DollarSign className="w-3 h-3 mr-1 text-slate-400" /> {job.salary_range}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Module 7 Deliverable Action: Generate / View Prep Pack */}
                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                      {isInterview ? (
                        job.has_prep_pack ? (
                          <button
                            onClick={() => handleOpenPrepPack(job)}
                            className="flex items-center space-x-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            <span>View Prep Pack</span>
                          </button>
                        ) : (
                          <button
                            onClick={() => handleGeneratePrepPack(job)}
                            className="flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg text-xs font-bold shadow hover:opacity-90 transition-opacity"
                          >
                            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                            <span>Generate Prep Pack</span>
                          </button>
                        )
                      ) : (
                        <button
                          onClick={() => handleStatusChange(job.id, 'Interview')}
                          className="text-[11px] text-slate-500 hover:text-indigo-600 font-medium"
                        >
                          Mark as Interview to Generate Prep
                        </button>
                      )}

                      <button
                        onClick={() => handleDeleteJob(job.id)}
                        className="text-slate-400 hover:text-rose-600 p-1 rounded hover:bg-slate-100 transition-colors"
                        title="Delete application"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="border border-dashed border-slate-200 rounded-xl p-8 text-center space-y-2 bg-white">
              <Briefcase className="w-8 h-8 text-slate-300 mx-auto" />
              <p className="text-sm font-medium text-slate-700">No job applications tracked yet</p>
              <p className="text-xs text-slate-400">
                Click "Add Application" above and mark status as "Interview" to generate checkable prep packs.
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Prep Pack Checklist View */}
        <div className="lg:col-span-2 space-y-4">
          {selectedJob ? (
            <div className="space-y-4">
              <div className="bg-slate-900 text-white rounded-xl p-5 shadow-sm flex items-center justify-between">
                <div>
                  <div className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">
                    {selectedJob.company_name}
                  </div>
                  <h2 className="text-xl font-bold text-white">{selectedJob.job_title}</h2>
                </div>

                {!prepPack && !isGenerating && (
                  <button
                    onClick={() => handleGeneratePrepPack(selectedJob)}
                    className="flex items-center space-x-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-colors"
                  >
                    <Sparkles className="w-4 h-4 text-amber-300" />
                    <span>Generate Prep Pack</span>
                  </button>
                )}
              </div>

              {isGenerating ? (
                <div className="bg-white border border-slate-200 rounded-xl p-12 text-center space-y-3 shadow-sm">
                  <Sparkles className="w-8 h-8 text-indigo-600 animate-spin mx-auto" />
                  <div className="font-bold text-slate-800 text-base">Generating Tailored Prep Pack...</div>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Analyzing Job Description and matching candidate resume bullets for STAR answers and company context.
                  </p>
                </div>
              ) : prepError ? (
                <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-xs text-rose-700">
                  {prepError}
                </div>
              ) : prepPack ? (
                <PrepPackChecklist prepPack={prepPack} onItemUpdate={handleItemUpdate} />
              ) : (
                <div className="bg-white border border-dashed border-slate-200 rounded-xl p-12 text-center space-y-3">
                  <Sparkles className="w-8 h-8 text-slate-300 mx-auto" />
                  <div className="font-semibold text-slate-800 text-sm">Prep Pack Ready to Generate</div>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto">
                    Click the button above to generate technical/behavioral questions, STAR draft answers, and company notes.
                  </p>
                  <button
                    onClick={() => handleGeneratePrepPack(selectedJob)}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold"
                  >
                    Generate Prep Pack Now
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white border border-dashed border-slate-200 rounded-xl p-16 text-center space-y-3">
              <Briefcase className="w-10 h-10 text-slate-300 mx-auto" />
              <h3 className="font-bold text-slate-800 text-base">Select a Job Application</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Select any application on the left (or mark status as "Interview") to open its checkable interview prep pack.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Add Job Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">Add New Job Application</h2>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateJob} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Company Name</label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="e.g. Stripe"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Job Title</label>
                  <input
                    type="text"
                    required
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g. Senior Backend Engineer"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Job Description (JD)</label>
                <textarea
                  rows={4}
                  required
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste key responsibilities, requirements, and tech stack from job post..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full px-2 py-2 border border-slate-300 rounded-lg text-xs bg-white"
                  >
                    <option value="Applied">Applied</option>
                    <option value="Interview">Interview 🔥</option>
                    <option value="Offered">Offered 🎉</option>
                    <option value="Rejected">Rejected</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="Remote / SF"
                    className="w-full px-2 py-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Salary</label>
                  <input
                    type="text"
                    value={salaryRange}
                    onChange={(e) => setSalaryRange(e.target.value)}
                    placeholder="$150k - $180k"
                    className="w-full px-2 py-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingJob}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-colors disabled:opacity-50"
                >
                  {isSubmittingJob ? 'Saving...' : 'Add Application'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Resume Manager Modal */}
      {showResumeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 max-w-xl w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">Manage Candidate Resume</h2>
              <button onClick={() => setShowResumeModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-500">
              Claude uses your actual resume bullets to match JD requirements and generate STAR draft answers.
            </p>

            <textarea
              rows={8}
              value={resumeContent}
              onChange={(e) => setResumeContent(e.target.value)}
              placeholder="Paste your key resume bullets, past project metrics, and technical skills here..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
            />

            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setShowResumeModal(false)}
                className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-medium text-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveResume}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold"
              >
                Save Resume Content
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobTrackerPage;
