import { useState, useRef } from 'react'; // Added useRef
import '../App.css';
import { useNavigate } from "react-router-dom";

function ResumeForm() {
  const [formData, setFormData] = useState({ jobTitle: '', minExperience: 2,shortlistedCandidates:0 });
  const [skillInput, setSkillInput] = useState('');
  const [skills, setSkills] = useState([]);
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles([...files, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && skillInput.trim()) {
      e.preventDefault();
      if (!skills.includes(skillInput.trim())) setSkills([...skills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  
  const formDataToSend = new FormData();
  formDataToSend.append('job_title', formData.jobTitle);
  formDataToSend.append('experience', formData.minExperience);
  formDataToSend.append('shortListCandidates', formData.shortlistedCandidates);
  formDataToSend.append('skills', JSON.stringify(skills));
  
  files.forEach((file) => {
    formDataToSend.append('files', file);
  });

  try {
    const response = await fetch('http://localhost:8000/process-resumes', {
      method: 'POST',
      body: formDataToSend,
    });
    const result = await response.json();
    navigate("/results", {
    state: {
      candidates: result.candidates,
    },
  });  } catch (error) {
    console.error("Error connecting to backend:", error);
  }
};

  return (
    <div className="container">
      <header>
        <h1>AI Resume Screener</h1>
        <p>Upload resumes and find the best fit</p>
      </header>

      <form className="screening-form" onSubmit={handleSubmit}>
        
        <div className="form-group">
          <label>Upload Resumes</label>
          <div className="upload-section">
            <button 
              type="button" 
              className="upload-btn" 
              onClick={() => fileInputRef.current.click()}
            >
              Upload Files
            </button>
            <input 
              type="file" 
              multiple  
              hidden 
              ref={fileInputRef} 
              onChange={handleFileChange} 
            />
            
            {files.length > 0 && (
              <ul className="file-list">
                {files.map((file, index) => (
                  <li key={index}>
                    <span>{file.name}</span>
                    <button type="button" onClick={() => removeFile(index)}>&times;</button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div className="form-group">
          <label>Job Title</label>
          <input type="text" value={formData.jobTitle} onChange={(e) => setFormData({...formData, jobTitle: e.target.value})} required />
        </div>
        <div className="form-group">
          <label>Number of candidates to shortlist</label>
          <input type="number" value={formData.shortlistedCandidates} onChange={(e) => setFormData({...formData, shortlistedCandidates: e.target.value})} required />
        </div>

        <div className="form-group">
          <label>Min Experience: {formData.minExperience} years</label>
          <input type="range" min="0" max="15" step="0.5" value={formData.minExperience} onChange={(e) => setFormData({...formData, minExperience: e.target.value})} />
        </div>

        <div className="form-group">
          <label>Skills Required</label>
          <div className="tag-container">
            {skills.map(skill => (
              <span key={skill} className="tag">
                {skill}
                <button type="button" onClick={() => setSkills(skills.filter(s => s !== skill))}>&times;</button>
              </span>
            ))}
            <input value={skillInput} onChange={(e) => setSkillInput(e.target.value)} onKeyDown={handleKeyDown} placeholder="Add skill..." />
          </div>
        </div>
        <button type="submit" className="submit-btn">Process & Search</button>
      </form>
    </div>
  );
}
export default ResumeForm;