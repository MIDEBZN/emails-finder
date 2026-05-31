import { useState } from 'react'
import './index.css'

function App() {
  const [title, setTitle] = useState('Data Scientist')
  const [location, setLocation] = useState('Canada')
  const [maxResults, setMaxResults] = useState(10)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState([])
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!title) return
    
    setIsLoading(true)
    setHasSearched(true)
    
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, location, max_results: parseInt(maxResults) || 10 }),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      
      // Ensure each job has a unique ID for React keys
      const formattedData = data.map((job, index) => ({
        id: index + 1,
        title: job.title,
        company: job.company,
        location: job.location,
        emails: job.emails.map(e => e.email), // Extract string emails from ExtractedEmail object
        url: job.url
      }));
      
      setResults(formattedData);
    } catch (error) {
      console.error("Failed to fetch live data:", error);
      // Fallback to empty results if server fails
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }

  const copyToClipboard = (email) => {
    navigator.clipboard.writeText(email);
    // In a real app we would show a toast notification here
  }

  const exportToCSV = () => {
    const csvRows = [];
    csvRows.push(['Job Title', 'Company', 'Location', 'URL', 'Emails'].join(','));
    
    results.filter(job => job.emails && job.emails.length > 0).forEach(job => {
      const emailStr = job.emails.join('; ');
      const row = [
        `"${job.title.replace(/"/g, '""')}"`,
        `"${job.company.replace(/"/g, '""')}"`,
        `"${job.location.replace(/"/g, '""')}"`,
        `"${job.url}"`,
        `"${emailStr}"`
      ];
      csvRows.push(row.join(','));
    });
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `IntelSearch_Leads_${title.replace(/\s+/g, '_')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const totalEmails = results.reduce((acc, job) => acc + job.emails.length, 0);

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo-container">
          <h1>IntelSearch CA</h1>
        </div>
        <div style={{color: 'var(--text-muted)', fontSize: '0.9rem', display: 'flex', gap: '2rem'}}>
          <span>Professional Intelligence System</span>
          <span>B2B Email Discovery</span>
        </div>
      </header>

      <main className="main-content">
        <section className="search-section">
          <div className="search-header">
            <h2>Find Direct Application Contacts</h2>
            <p>Aggregating Canadian ATS postings and extracting hidden recruiter emails.</p>
          </div>
          
          <form className="search-controls" onSubmit={handleSearch}>
            <div className="input-group">
              <input 
                type="text" 
                placeholder="Job Title (e.g., Software Engineer)" 
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="input-group">
              <input 
                type="text" 
                placeholder="Location (e.g., Canada, Toronto)" 
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
            <div className="input-group">
              <input 
                type="number" 
                placeholder="Max Results (e.g. 10)" 
                value={maxResults}
                onChange={(e) => setMaxResults(e.target.value)}
                min="1"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search Engine'}
              {!isLoading && (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              )}
            </button>
          </form>
        </section>

        {isLoading ? (
          <div className="loader-container">
            <div className="loader"></div>
            <p className="pulse-text">Scraping ATS platforms and parsing descriptions...</p>
          </div>
        ) : hasSearched && (
          <section className="results-section">
            <div className="results-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', background: 'rgba(20, 26, 40, 0.8)', padding: '1.5rem', borderRadius: '16px', border: '1px solid var(--border-color)', backdropFilter: 'blur(10px)' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--text-main)', fontFamily: "'Outfit', sans-serif" }}>Extracted Results</h3>
                <p style={{ margin: '0.5rem 0 0', color: 'var(--success)', fontWeight: '500', fontSize: '1.1rem' }}>
                  ✅ Successfully scraped {totalEmails} actionable emails from {results.length} listings.
                </p>
              </div>
              <button onClick={exportToCSV} className="btn-primary" style={{ background: 'linear-gradient(135deg, #06d6a0, #04b285)', boxShadow: '0 4px 15px rgba(6, 214, 160, 0.3)' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '0.5rem' }}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Export CSV
              </button>
            </div>
            
            <div className="results-grid">
              {results.map((job, index) => (
                <div 
                  className="job-card" 
                  key={job.id}
                  style={{ animationDelay: `${index * 0.15}s` }}
                >
                  <div className="job-header">
                    <div>
                      <h4 className="job-title">{job.title}</h4>
                      <p className="job-company">{job.company}</p>
                    </div>
                  </div>
                  
                  <div className="job-location">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    {job.location}
                  </div>

                  <div className="emails-section">
                    <h5 className="emails-title">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                        <polyline points="22,6 12,13 2,6"></polyline>
                      </svg>
                      Direct Contacts
                    </h5>
                    
                    <div className="email-list">
                      {job.emails.length > 0 ? (
                        job.emails.map((email, idx) => (
                          <div 
                            className="email-tag" 
                            key={idx}
                            onClick={() => copyToClipboard(email)}
                            title="Click to copy"
                          >
                            <span>{email}</span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                          </div>
                        ))
                      ) : (
                        <p className="no-email">No emails found in description</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
