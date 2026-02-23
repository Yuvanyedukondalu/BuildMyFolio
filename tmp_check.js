
    // ─── State ─────────────────────────────────────────────────────────────────
    const state = {
      skills: [],
      certifications: [],
      education: [],
      experience: [],
      projects: [],
      generatedData: null,
      latestPortfolio: null,
      activeTab: 'resume',
      options: { resume: true, cover: true, portfolio: true },
    };

    const API_BASE = 'http://localhost:8000';

    // ─── Nav ───────────────────────────────────────────────────────────────────
    document.querySelectorAll('[data-panel]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-panel]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const panel = btn.dataset.panel;
        document.getElementById('panel-builder').style.display = panel === 'builder' ? 'grid' : 'none';
        document.getElementById('panel-ats').style.display = panel === 'ats' ? 'flex' : 'none';
        document.getElementById('panel-about').style.display = panel === 'about' ? 'block' : 'none';
      });
    });

    // ─── Output Tabs ───────────────────────────────────────────────────────────
    document.querySelectorAll('[data-tab]').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('[data-tab]').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        state.activeTab = tab.dataset.tab;
        if (state.generatedData) renderOutput(state.generatedData);
      });
    });

    // ─── Section Toggle ─────────────────────────────────────────────────────────
    function toggleSection(id) {
      const el = document.getElementById('section-' + id);
      const toggle = document.getElementById('toggle-' + id);
      const hidden = el.style.display === 'none';
      el.style.display = hidden ? 'flex' : 'none';
      toggle.classList.toggle('open', hidden);
    }

    // ─── Generate Options ───────────────────────────────────────────────────────
    function toggleOption(opt) {
      state.options[opt] = !state.options[opt];
      document.getElementById('opt-' + opt).classList.toggle('selected', state.options[opt]);
    }

    // ─── Tags Input ─────────────────────────────────────────────────────────────
    function initTagInput(inputId, containerId, stateKey) {
      const input = document.getElementById(inputId);
      input.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ',') {
          e.preventDefault();
          const val = input.value.trim().replace(/,$/, '');
          if (val && !state[stateKey].includes(val)) {
            state[stateKey].push(val);
            renderTag(containerId, stateKey, val);
          }
          input.value = '';
        } else if (e.key === 'Backspace' && !input.value && state[stateKey].length) {
          const last = state[stateKey].pop();
          document.getElementById(containerId).querySelector(`.tag[data-val="${CSS.escape(last)}"]`)?.remove();
        }
      });
      document.getElementById(containerId).addEventListener('click', e => input.focus());
    }

    function renderTag(containerId, stateKey, val) {
      const container = document.getElementById(containerId);
      const input = container.querySelector('.tag-input');
      const tag = document.createElement('span');
      tag.className = 'tag';
      tag.dataset.val = val;
      tag.innerHTML = `${val} <span class="tag-remove" onclick="removeTag('${containerId}','${stateKey}','${val}',this.parentElement)">✕</span>`;
      container.insertBefore(tag, input);
    }

    function removeTag(containerId, stateKey, val, el) {
      state[stateKey] = state[stateKey].filter(s => s !== val);
      el.remove();
    }

    initTagInput('skillInput', 'skillsContainer', 'skills');
    initTagInput('certInput', 'certContainer', 'certifications');

    // ─── Education ──────────────────────────────────────────────────────────────
    function addEducation() {
      const id = Date.now();
      state.education.push({ id });
      renderEducationItem(id);
    }

    function renderEducationItem(id) {
      const el = document.createElement('div');
      el.className = 'list-item';
      el.id = 'edu-' + id;
      el.innerHTML = `
    <button class="item-remove" onclick="removeItem('education','${id}','edu-${id}')">✕</button>
    <div style="display:flex;flex-direction:column;gap:0.6rem;">
      <div class="form-row">
        <div class="field"><label>Institution</label><input type="text" onchange="updateItem('education','${id}','institution',this.value)" placeholder="IIT Hyderabad" /></div>
        <div class="field"><label>Degree</label><input type="text" onchange="updateItem('education','${id}','degree',this.value)" placeholder="B.Tech" /></div>
      </div>
      <div class="form-row">
        <div class="field"><label>Field of Study</label><input type="text" onchange="updateItem('education','${id}','field',this.value)" placeholder="Computer Science" /></div>
        <div class="field"><label>GPA</label><input type="number" step="0.1" min="0" max="10" onchange="updateItem('education','${id}','gpa',parseFloat(this.value))" placeholder="8.5" /></div>
      </div>
      <div class="form-row">
        <div class="field"><label>Start Year</label><input type="number" onchange="updateItem('education','${id}','start_year',parseInt(this.value))" placeholder="2021" /></div>
        <div class="field"><label>End Year</label><input type="number" onchange="updateItem('education','${id}','end_year',parseInt(this.value))" placeholder="2025" /></div>
      </div>
    </div>
  `;
      document.getElementById('educationList').appendChild(el);
    }

    // ─── Experience ─────────────────────────────────────────────────────────────
    function addExperience() {
      const id = Date.now();
      state.experience.push({ id });
      renderExperienceItem(id);
    }

    function renderExperienceItem(id) {
      const el = document.createElement('div');
      el.className = 'list-item';
      el.id = 'exp-' + id;
      el.innerHTML = `
    <button class="item-remove" onclick="removeItem('experience','${id}','exp-${id}')">✕</button>
    <div style="display:flex;flex-direction:column;gap:0.6rem;">
      <div class="form-row">
        <div class="field"><label>Company</label><input type="text" onchange="updateItem('experience','${id}','company',this.value)" placeholder="Google" /></div>
        <div class="field"><label>Role</label><input type="text" onchange="updateItem('experience','${id}','role',this.value)" placeholder="Software Intern" /></div>
      </div>
      <div class="form-row">
        <div class="field"><label>Start Date</label><input type="text" onchange="updateItem('experience','${id}','start_date',this.value)" placeholder="May 2024" /></div>
        <div class="field"><label>End Date</label><input type="text" onchange="updateItem('experience','${id}','end_date',this.value)" placeholder="Aug 2024" /></div>
      </div>
      <div class="field"><label>Description</label><textarea onchange="updateItem('experience','${id}','description',this.value)" placeholder="Describe what you did, your impact, and achievements..."></textarea></div>
      <div class="field"><label>Technologies Used</label><input type="text" onchange="updateItem('experience','${id}','technologies',this.value.split(',').map(t=>t.trim()))" placeholder="Python, React, PostgreSQL" /></div>
    </div>
  `;
      document.getElementById('experienceList').appendChild(el);
    }

    // ─── Projects ───────────────────────────────────────────────────────────────
    function addProject() {
      const id = Date.now();
      state.projects.push({ id });
      renderProjectItem(id);
    }

    function renderProjectItem(id) {
      const el = document.createElement('div');
      el.className = 'list-item';
      el.id = 'proj-' + id;
      el.innerHTML = `
    <button class="item-remove" onclick="removeItem('projects','${id}','proj-${id}')">✕</button>
    <div style="display:flex;flex-direction:column;gap:0.6rem;">
      <div class="form-row">
        <div class="field"><label>Project Name</label><input type="text" onchange="updateItem('projects','${id}','name',this.value)" placeholder="BuildMyFolio Assistant" /></div>
        <div class="field"><label>GitHub URL</label><input type="url" onchange="updateItem('projects','${id}','github_url',this.value)" placeholder="github.com/..." /></div>
      </div>
      <div class="field"><label>Description</label><textarea onchange="updateItem('projects','${id}','description',this.value)" placeholder="What does this project do? What problem does it solve?"></textarea></div>
      <div class="form-row">
        <div class="field"><label>Technologies</label><input type="text" onchange="updateItem('projects','${id}','technologies',this.value.split(',').map(t=>t.trim()))" placeholder="React, Python, ML" /></div>
        <div class="field"><label>Live URL</label><input type="url" onchange="updateItem('projects','${id}','live_url',this.value)" placeholder="https://..." /></div>
      </div>
      <div class="field"><label>Impact / Result</label><input type="text" onchange="updateItem('projects','${id}','impact',this.value)" placeholder="Reduced time by 60%, helped 100+ users..." /></div>
    </div>
  `;
      document.getElementById('projectsList').appendChild(el);
    }

    function updateItem(arr, id, key, val) {
      const item = state[arr].find(i => String(i.id) === String(id));
      if (item) item[key] = val;
    }

    function removeItem(arr, id, elId) {
      state[arr] = state[arr].filter(i => String(i.id) !== String(id));
      document.getElementById(elId)?.remove();
    }

    // ─── Build Profile ───────────────────────────────────────────────────────────
    function buildProfile() {
      return {
        name: document.getElementById('name').value || 'Student',
        email: document.getElementById('email').value || 'email@example.com',
        phone: document.getElementById('phone').value,
        location: document.getElementById('location').value,
        linkedin: document.getElementById('linkedin').value,
        github: document.getElementById('github').value,
        target_role: document.getElementById('targetRole').value || 'Software Developer',
        target_industry: document.getElementById('targetIndustry').value,
        skills: state.skills,
        certifications: state.certifications,
        education: state.education.map(e => ({
          institution: e.institution || 'University',
          degree: e.degree || 'Bachelor\'s',
          field: e.field || 'Computer Science',
          start_year: e.start_year || 2021,
          end_year: e.end_year,
          gpa: e.gpa,
          achievements: [],
        })).filter(e => e.institution !== 'University' || state.education.length === 1),
        experience: state.experience.map(e => ({
          company: e.company || '',
          role: e.role || '',
          start_date: e.start_date || '',
          end_date: e.end_date || 'Present',
          description: e.description || '',
          technologies: e.technologies || [],
        })).filter(e => e.company || e.role),
        projects: state.projects.map(p => ({
          name: p.name || 'Project',
          description: p.description || '',
          technologies: p.technologies || [],
          github_url: p.github_url,
          live_url: p.live_url,
          impact: p.impact,
        })).filter(p => p.name !== 'Project' || p.description),
      };
    }

    // ─── Generate Documents ──────────────────────────────────────────────────────
    async function generateDocuments() {
      const btn = document.getElementById('generateBtn');
      btn.disabled = true;

      // Show loading
      const output = document.getElementById('outputContent');
      output.innerHTML = `
    <div class="loading-overlay">
      <div class="spinner"></div>
      <div class="loading-steps" id="loadingSteps">
        <div class="loading-step active" style="animation-delay:0s">🧠 Analyzing your profile...</div>
        <div class="loading-step" style="animation-delay:0.4s">🎯 Matching keywords from job description...</div>
        <div class="loading-step" style="animation-delay:0.8s">✍️ Crafting personalized content...</div>
        <div class="loading-step" style="animation-delay:1.2s">⚡ Optimizing for ATS systems...</div>
        <div class="loading-step" style="animation-delay:1.6s">✨ Finalizing documents...</div>
      </div>
    </div>
  `;

      // Animate loading steps
      const steps = output.querySelectorAll('.loading-step');
      let stepIdx = 0;
      const stepTimer = setInterval(() => {
        if (stepIdx > 0) steps[stepIdx - 1]?.classList.replace('active', 'done');
        if (stepIdx < steps.length) steps[stepIdx]?.classList.add('active');
        stepIdx++;
        if (stepIdx > steps.length) clearInterval(stepTimer);
      }, 600);

      const profile = buildProfile();
      const jobDesc = document.getElementById('jobDescription').value;
      const company = document.getElementById('companyName').value;
      const tone = document.getElementById('tone').value;

      // Make sure education has at least one entry
      if (profile.education.length === 0) {
        profile.education = [{ institution: 'Your University', degree: "Bachelor's", field: 'Computer Science', start_year: 2021 }];
      }

      try {
        const response = await fetch(`${API_BASE}/api/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            profile,
            generate_resume: state.options.resume,
            generate_cover_letter: state.options.cover && !!company,
            generate_portfolio: state.options.portfolio,
            job_description: jobDesc || null,
            company_name: company || null,
            tone,
          }),
        });

        clearInterval(stepTimer);

        if (!response.ok) throw new Error('API error: ' + response.status);

        const data = await response.json();
        state.generatedData = data.data;
        renderOutput(data.data);
      } catch (err) {
        // Fallback: generate mock data client-side
        clearInterval(stepTimer);
        const mockData = generateMockData(profile, jobDesc, company, tone);
        state.generatedData = mockData;
        renderOutput(mockData);
      }

      btn.disabled = false;
    }

    // ─── Mock Data Generator (client-side fallback) ───────────────────────────
    function generateMockData(profile, jobDesc, company, tone) {
      const skillCategories = {
        languages: profile.skills.filter(s => ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'Go', 'Rust', 'Swift', 'Kotlin', 'R'].includes(s)),
        frameworks: profile.skills.filter(s => ['React', 'Next.js', 'Vue', 'Angular', 'FastAPI', 'Django', 'Flask', 'Express', 'TensorFlow', 'PyTorch'].includes(s)),
        databases: profile.skills.filter(s => ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite'].includes(s)),
        cloud: profile.skills.filter(s => ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes'].includes(s)),
        tools: profile.skills.filter(s => ['Git', 'GitHub', 'Jira', 'Figma', 'Linux', 'REST API'].includes(s)),
        other: profile.skills.filter(s => !['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'Go', 'React', 'Next.js', 'Vue', 'Angular', 'FastAPI', 'Django', 'Flask', 'TensorFlow', 'PyTorch', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git'].includes(s)),
      };

      const skillsOrg = Object.fromEntries(Object.entries(skillCategories).filter(([, v]) => v.length));

      const targetRole = profile.target_role || 'Software Developer';
      const skillStr = profile.skills.slice(0, 4).join(', ') || 'Python, JavaScript, React';
      const edu = profile.education[0] || {};
      const degree = edu.degree || "Bachelor's";
      const field = edu.field || 'Computer Science';

      const summary = `Results-driven ${targetRole} with a ${degree} in ${field} and strong academic foundation in the ${profile.target_industry} industry. Proficient in ${skillStr}, with a proven track record of delivering impactful solutions. Seeking to leverage technical expertise and problem-solving abilities.`;

      const enhancedExp = (profile.experience || []).map(exp => ({
        ...exp,
        bullets: [
          `Built and maintained ${exp.technologies?.join(', ') || 'key systems'} applications with focus on performance and scalability`,
          `${exp.description?.slice(0, 120) || 'Developed scalable solutions contributing to team goals'} — [Add specific metric]`,
          `Collaborated with cross-functional teams using Agile methodologies to deliver features on schedule`,
        ],
      }));

      const enhancedProjects = (profile.projects || []).map((p, i) => ({
        ...p,
        highlight: i < 2,
        relevance_score: 3 - i,
        card_color: ['#b794f6', '#93c5fd', '#c4b5fd', '#a5b4fc', '#7dd3fc'][i % 5],
        category: 'Software Engineering',
        tags: p.technologies?.slice(0, 4) || [],
        generated_impact: `Implemented using ${p.technologies?.length || 3} technologies, demonstrating full-stack capabilities`,
      }));

      const coverLetter = company ? {
        recipient: `Hiring Manager, ${company}`,
        subject: `Application for ${targetRole} Position`,
        paragraphs: [
          `I am writing to express my strong interest in the ${targetRole} position at ${company}. With a ${degree} in ${field} and hands-on experience in ${skillStr}, I am confident in my ability to make a meaningful contribution to your team.`,
          profile.experience?.length > 0
            ? `In my role as ${profile.experience[0].role} at ${profile.experience[0].company}, I developed ${profile.experience[0].description?.slice(0, 120) || 'strong technical skills'}. This experience strengthened my expertise in ${profile.experience[0].technologies?.slice(0, 3).join(', ') || skillStr}.`
            : `Through my academic projects and self-directed learning, I have developed proficiency in ${skillStr}. My coursework has given me a solid theoretical foundation that I am eager to apply in a professional setting.`,
          profile.projects?.length > 0
            ? `One of my key projects, "${profile.projects[0].name}", involved ${profile.projects[0].description?.slice(0, 120) || 'building an innovative solution'}. Built using ${profile.projects[0].technologies?.slice(0, 4).join(', ') || skillStr}, this project demonstrates my ability to deliver end-to-end solutions.`
            : '',
          `I look forward to discussing how my skills align with the ${company} team. I am particularly drawn to ${company}'s work and believe my background in ${profile.skills.slice(0, 2).join(' and ')} would enable me to contribute effectively from day one. Thank you for considering my application.`,
        ].filter(Boolean),
        signature: profile.name,
        word_count: 280,
      } : null;

      const portfolioStats = {
        projects_built: profile.projects?.length || 0,
        technologies: profile.skills?.length || 0,
        years_coding: Math.max(1, profile.experience?.length || 1) + 1,
        certifications: profile.certifications?.length || 0,
      };

      const skillsViz = Object.entries(skillsOrg).map(([cat, skills], i) => ({
        category: cat.charAt(0).toUpperCase() + cat.slice(1),
        skills: skills.slice(0, 5),
        proficiency: Math.max(55, 90 - i * 8),
        count: skills.length,
      }));

      return {
        resume: {
          header: { name: profile.name, email: profile.email, phone: profile.phone, location: profile.location, linkedin: profile.linkedin, github: profile.github },
          summary,
          skills: skillsOrg,
          experience: enhancedExp,
          projects: enhancedProjects,
          education: profile.education,
          certifications: profile.certifications,
        },
        cover_letter: coverLetter,
        portfolio: {
          bio: {
            headline: `${targetRole} & Problem Solver`,
            tagline: `Building impactful solutions with ${profile.skills[0] || 'code'}`,
            about: `Hi, I'm ${profile.name} — a ${targetRole} passionate about building impactful software. I hold a ${degree} in ${field} and have built ${profile.projects?.length || 0}+ projects using ${skillStr}. I thrive at the intersection of technical excellence and creative problem-solving.`,
            interests: ['Open Source', 'Tech Innovation', 'AI/ML', 'Cloud Computing'].slice(0, 4),
          },
          featured_projects: enhancedProjects,
          skills_visualization: skillsViz,
          stats: portfolioStats,
          contact: { name: profile.name, email: profile.email, github: profile.github, linkedin: profile.linkedin },
        },
        skills_analysis: {
          total_skills: profile.skills?.length || 0,
          matching_skills: profile.skills?.slice(0, 5) || [],
          skill_gaps: jobDesc ? ['Kubernetes', 'Terraform', 'GraphQL'].slice(0, 3) : [],
          match_percentage: 75,
          top_skills: profile.skills?.slice(0, 8) || [],
          learning_suggestions: ['Consider exploring cloud certifications', 'Add testing frameworks to your skills'],
        },
      };
    }

    // ─── Render Output ───────────────────────────────────────────────────────────
    function renderOutput(data) {
      const output = document.getElementById('outputContent');
      const tab = state.activeTab;

      if (tab === 'resume' && data.resume) {
        output.innerHTML = renderResume(data.resume);
      } else if (tab === 'cover' && data.cover_letter) {
        output.innerHTML = renderCoverLetter(data.cover_letter);
      } else if (tab === 'portfolio' && data.portfolio) {
        output.innerHTML = renderPortfolio(data.portfolio);
      } else if (tab === 'analysis' && data.skills_analysis) {
        output.innerHTML = renderAnalysis(data.skills_analysis);
      } else {
        output.innerHTML = `<div class="empty-state"><div class="empty-icon">ℹ️</div><div class="empty-title">Not generated</div><div class="empty-sub">Enable this option and regenerate.</div></div>`;
      }
    }

    // ─── Resume Renderer ─────────────────────────────────────────────────────────
    function renderResume(resume) {
      const h = resume.header || {};
      const contactItems = [
        h.email && `<span class="contact-item">📧 ${h.email}</span>`,
        h.phone && `<span class="contact-item">📱 ${h.phone}</span>`,
        h.location && `<span class="contact-item">📍 ${h.location}</span>`,
        h.linkedin && `<span class="contact-item">🔗 LinkedIn</span>`,
        h.github && `<span class="contact-item">💻 GitHub</span>`,
      ].filter(Boolean).join('');

      const skillsHtml = Object.entries(resume.skills || {}).map(([cat, skills]) =>
        skills.map(s => `<span class="skill-tag ${cat}">${s}</span>`).join('')
      ).join('');

      const expHtml = (resume.experience || []).map(exp => `
    <div class="exp-item">
      <div class="exp-title-row">
        <div>
          <div class="exp-role">${exp.role || ''}</div>
          <div class="exp-company">${exp.company || ''}</div>
        </div>
        <div class="exp-dates">${exp.start_date || ''} — ${exp.end_date || 'Present'}</div>
      </div>
      <ul class="exp-bullets">
        ${(exp.bullets || [exp.description]).filter(Boolean).map(b => `<li>${b}</li>`).join('')}
      </ul>
      ${exp.technologies?.length ? `<div class="exp-techs">${exp.technologies.map(t => `<span class="tech-pill">${t}</span>`).join('')}</div>` : ''}
    </div>
  `).join('');

      const projHtml = (resume.projects || []).map(proj => `
    <div class="proj-item">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div class="proj-name">${proj.name || ''}</div>
        ${proj.highlight ? '<span class="pill-label pill-success">✦ Featured</span>' : ''}
      </div>
      <div class="proj-desc">${proj.description || proj.generated_impact || ''}</div>
      <div class="exp-techs">${(proj.technologies || []).map(t => `<span class="tech-pill">${t}</span>`).join('')}</div>
      <div class="proj-links">
        ${proj.github_url ? `<a class="proj-link" href="${proj.github_url}" target="_blank">⊕ GitHub</a>` : ''}
        ${proj.live_url ? `<a class="proj-link" href="${proj.live_url}" target="_blank">⊞ Live Demo</a>` : ''}
      </div>
    </div>
  `).join('');

      const eduHtml = (resume.education || []).map(edu => `
    <div class="edu-item">
      <div class="edu-degree">${edu.degree || ''} in ${edu.field || ''}</div>
      <div class="edu-institution">${edu.institution || ''}</div>
      <div class="edu-meta">${edu.start_year || ''} — ${edu.end_year || 'Present'} ${edu.gpa ? '· GPA: ' + edu.gpa : ''}</div>
    </div>
  `).join('');

      const certHtml = (resume.certifications || []).length ? `
    <div class="resume-section">
      <div class="rs-title">Certifications</div>
      <div class="skills-grid">${(resume.certifications || []).map(c => `<span class="skill-tag other">${c}</span>`).join('')}</div>
    </div>
  ` : '';

      return `
    <div class="export-bar">
      <button class="export-btn" onclick="copyResume()">📋 Copy Text</button>
      <button class="export-btn primary" onclick="downloadResumeDoc()">⬇ Download Resume</button>
    </div>
    <div class="resume-doc" id="resumeDoc">
      <div class="resume-header-section">
        <div class="resume-name">${h.name || 'Your Name'}</div>
        <div class="resume-target">${document.getElementById('targetRole').value || 'Software Developer'}</div>
        <div class="resume-contact">${contactItems}</div>
      </div>
      <div class="resume-body">
        ${resume.summary ? `<div class="resume-section"><div class="rs-title">Professional Summary</div><div class="rs-summary">${resume.summary}</div></div>` : ''}
        ${skillsHtml ? `<div class="resume-section"><div class="rs-title">Technical Skills</div><div class="skills-grid">${skillsHtml}</div></div>` : ''}
        ${expHtml ? `<div class="resume-section"><div class="rs-title">Work Experience</div>${expHtml}</div>` : ''}
        ${projHtml ? `<div class="resume-section"><div class="rs-title">Projects</div>${projHtml}</div>` : ''}
        ${eduHtml ? `<div class="resume-section"><div class="rs-title">Education</div>${eduHtml}</div>` : ''}
        ${certHtml}
      </div>
    </div>
  `;
    }

    // ─── Cover Letter Renderer ───────────────────────────────────────────────────
    function renderCoverLetter(cl) {
      if (!cl) return `<div class="empty-state"><div class="empty-icon">✉️</div><div class="empty-title">No cover letter generated</div><div class="empty-sub">Enter a company name and regenerate.</div></div>`;

      const paras = (cl.paragraphs || []).filter(Boolean).map(p => `<p class="cl-para">${p}</p>`).join('');

      return `
    <div class="export-bar">
      <button class="export-btn" onclick="copyCoverLetter()">📋 Copy</button>
      <button class="export-btn primary" onclick="window.print()">⬇ Export</button>
    </div>
    <div class="cover-letter-doc">
      <div class="cl-subject">Cover Letter</div>
      <div class="cl-title">${cl.subject || 'Application Letter'}</div>
      <div style="color:var(--text3); font-size:0.8rem; margin-bottom:1.5rem; font-family:'JetBrains Mono',monospace;">${cl.recipient || ''}</div>
      <div class="divider"></div>
      <br/>
      ${paras}
      <br/>
      <div style="color:var(--text2); font-size:0.8rem;">Sincerely,</div>
      <div class="cl-sig">${cl.signature || 'Your Name'}</div>
      <br/>
      <div style="color:var(--text3); font-size:0.75rem; font-family:'JetBrains Mono',monospace;">${cl.word_count || 0} words · AI-optimized</div>
    </div>
  `;
    }

    // ─── Portfolio Renderer ──────────────────────────────────────────────────────
    function renderPortfolio(portfolio) {
      if (!portfolio) return '';
      state.latestPortfolio = portfolio;

      const bio = portfolio.bio || {};
      const stats = portfolio.stats || {};

      const statsHtml = `
    <div class="portfolio-stats">
      <div class="stat-card"><div class="stat-num">${stats.projects_built || 0}</div><div class="stat-label">Projects Built</div></div>
      <div class="stat-card"><div class="stat-num">${stats.technologies || 0}</div><div class="stat-label">Technologies</div></div>
      <div class="stat-card"><div class="stat-num">${stats.years_coding || 1}+</div><div class="stat-label">Years Coding</div></div>
      <div class="stat-card"><div class="stat-num">${stats.certifications || 0}</div><div class="stat-label">Certifications</div></div>
    </div>
  `;

      const projectCards = (portfolio.featured_projects || []).slice(0, 6).map(proj => `
    <div class="portfolio-proj-card" style="--card-color:${proj.card_color || '#b794f6'}">
      <div class="proj-card-cat">${proj.category || 'Engineering'}</div>
      <div class="proj-card-name">${proj.name || ''}</div>
      <div class="proj-card-desc">${(proj.description || '').slice(0, 120)}${(proj.description || '').length > 120 ? '...' : ''}</div>
      <div class="proj-card-tags">${(proj.tags || proj.technologies || []).slice(0, 4).map(t => `<span class="proj-tag">${t}</span>`).join('')}</div>
    </div>
  `).join('');

      const skillBars = (portfolio.skills_visualization || []).map(s => `
    <div class="skill-bar-item">
      <div class="skill-bar-header">
        <span>${s.category} <span style="color:var(--text3);font-size:0.7rem;">(${s.skills?.slice(0, 3).join(', ') || ''})</span></span>
        <span style="color:var(--accent2); font-family:'JetBrains Mono',monospace; font-size:0.8rem;">${s.proficiency}%</span>
      </div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:${s.proficiency}%"></div></div>
    </div>
  `).join('');

      return `
    <div class="export-bar">
      <button class="export-btn" onclick="openPortfolioFullPage()">↗ View Full Page</button>
      <button class="export-btn primary" onclick="downloadPortfolioZip()">⬇ Download Portfolio ZIP</button>
    </div>
    <div class="portfolio-preview">
      <div class="portfolio-hero">
        <div class="portfolio-name">${bio.headline || 'Developer'}</div>
        <div class="portfolio-tagline">${bio.tagline || ''}</div>
        <div style="font-size:0.875rem; color:var(--text2); max-width:600px; margin:0 auto; line-height:1.7;">${bio.about || ''}</div>
        <div style="display:flex; justify-content:center; gap:0.5rem; margin-top:1rem; flex-wrap:wrap;">
          ${(bio.interests || []).map(i => `<span class="pill-label pill-success">◎ ${i}</span>`).join('')}
        </div>
      </div>
      ${statsHtml}
      ${projectCards ? `<h3>Featured Projects</h3><div class="projects-grid">${projectCards}</div>` : ''}
      ${skillBars ? `<div class="skills-section"><h3 style="margin-bottom:1rem;">Skills Overview</h3><div class="skills-bars">${skillBars}</div></div>` : ''}
    </div>
  `;
    }

    // ─── Analysis Renderer ────────────────────────────────────────────────────────
    function renderAnalysis(analysis) {
      if (!analysis) return '';

      const matchPct = analysis.match_percentage || 0;
      const color = matchPct >= 70 ? '#34d399' : matchPct >= 50 ? '#fbbf24' : '#f87171';

      const matchedPills = (analysis.matching_skills || []).map(s => `<span class="kw-matched">✓ ${s}</span>`).join('');
      const gapPills = (analysis.skill_gaps || []).map(s => `<span class="kw-missing">✗ ${s}</span>`).join('');
      const topSkills = (analysis.top_skills || []).map(s => `<span class="kw-matched">⚡ ${s}</span>`).join('');
      const suggestions = (analysis.learning_suggestions || []).map(s => `<div class="rec-item"><span class="rec-icon">💡</span>${s}</div>`).join('');

      return `
    <div class="ats-panel">
      <div class="ats-score-ring">
        <div class="score-circle" style="border-color:${color}">
          <div class="score-num" style="color:${color}">${Math.round(matchPct)}%</div>
          <div class="score-label">Match</div>
        </div>
        <div style="font-size:0.875rem; color:var(--text2);">${matchPct >= 70 ? '✅ Strong alignment with target role' : matchPct >= 50 ? '⚠️ Good match — address gaps' : '🔴 Skill development needed'}</div>
      </div>
      <div class="ats-breakdown">
        <div class="breakdown-card"><div class="bd-label">Total Skills</div><div class="bd-value">${analysis.total_skills}</div></div>
        <div class="breakdown-card"><div class="bd-label">Matching Skills</div><div class="bd-value" style="color:var(--success)">${analysis.matching_skills?.length || 0}</div></div>
        <div class="breakdown-card"><div class="bd-label">Skill Gaps</div><div class="bd-value" style="color:var(--danger)">${analysis.skill_gaps?.length || 0}</div></div>
        <div class="breakdown-card"><div class="bd-label">Match Score</div><div class="bd-value" style="color:${color}">${Math.round(matchPct)}%</div></div>
      </div>
      ${topSkills ? `<h3>Your Top Skills</h3><div class="keyword-pills">${topSkills}</div>` : ''}
      ${matchedPills ? `<h3>Matching JD Skills</h3><div class="keyword-pills">${matchedPills}</div>` : ''}
      ${gapPills ? `<h3>Skill Gaps</h3><div class="keyword-pills">${gapPills}</div>` : ''}
      ${suggestions ? `<h3>Learning Recommendations</h3><div class="recs-list">${suggestions}</div>` : ''}
    </div>
  `;
    }

    // ─── ATS Check ────────────────────────────────────────────────────────────────
    async function runATSCheck() {
      const resume = document.getElementById('atsResume').value;
      const jd = document.getElementById('atsJD').value;
      const result = document.getElementById('atsResult');

      if (!resume || !jd) {
        result.innerHTML = '<div class="rec-item"><span class="rec-icon">⚠️</span>Please enter both resume text and job description.</div>';
        return;
      }

      result.innerHTML = '<div class="loading-overlay" style="height:80px;"><div class="spinner"></div></div>';

      try {
        const response = await fetch(`${API_BASE}/api/ats-score`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: resume, job_description: jd }),
        });

        if (!response.ok) throw new Error();

        const data = await response.json();
        const score = data.data;
        renderATSResult(result, score);
      } catch {
        // Mock ATS result
        const mockScore = {
          overall_score: 62,
          breakdown: { keyword_match: 58, format_score: 80, action_verbs: 60, quantification: 30 },
          matched_keywords: ['Python', 'React', 'API'],
          missing_keywords: ['Docker', 'Kubernetes', 'TypeScript'],
          recommendations: [
            'Add Docker and Kubernetes experience',
            'Quantify achievements with numbers (e.g., improved performance by 40%)',
            'Use more action verbs (Led, Built, Achieved)',
            'Add LinkedIn profile to resume',
          ]
        };
        renderATSResult(result, mockScore);
      }
    }

    function renderATSResult(container, score) {
      const color = score.overall_score >= 70 ? '#34d399' : score.overall_score >= 50 ? '#fbbf24' : '#f87171';
      container.innerHTML = `
    <div class="ats-panel">
      <div class="ats-score-ring">
        <div class="score-circle" style="border-color:${color}">
          <div class="score-num" style="color:${color}">${score.overall_score}</div>
          <div class="score-label">ATS Score</div>
        </div>
      </div>
      <div class="ats-breakdown">
        ${Object.entries(score.breakdown || {}).map(([k, v]) => `
          <div class="breakdown-card">
            <div class="bd-label">${k.replace(/_/g, ' ')}</div>
            <div class="bd-value" style="color:${v >= 70 ? '#34d399' : v >= 50 ? '#fbbf24' : '#f87171'}">${Math.round(v)}%</div>
          </div>
        `).join('')}
      </div>
      ${score.matched_keywords?.length ? `<h3>Matched Keywords</h3><div class="keyword-pills">${score.matched_keywords.map(k => `<span class="kw-matched">✓ ${k}</span>`).join('')}</div>` : ''}
      ${score.missing_keywords?.length ? `<h3>Missing Keywords</h3><div class="keyword-pills">${score.missing_keywords.map(k => `<span class="kw-missing">✗ ${k}</span>`).join('')}</div>` : ''}
      ${score.recommendations?.length ? `<h3>Recommendations</h3><div class="recs-list">${score.recommendations.map(r => `<div class="rec-item"><span class="rec-icon">💡</span>${r}</div>`).join('')}</div>` : ''}
    </div>
  `;
    }

    // ─── Export Utils ─────────────────────────────────────────────────────────────
    function copyResume() {
      const el = document.getElementById('resumeDoc');
      navigator.clipboard?.writeText(el?.innerText || '').then(() => alert('Resume copied to clipboard!'));
    }
    function copyCoverLetter() {
      const el = document.querySelector('.cover-letter-doc');
      navigator.clipboard?.writeText(el?.innerText || '').then(() => alert('Cover letter copied!'));
    }

    function sanitizeFilename(value) {
      return (value || 'resume').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    }

    function downloadResumeDoc() {
      const resumeEl = document.getElementById('resumeDoc');
      if (!resumeEl) {
        alert('Generate a resume first.');
        return;
      }

      const name = resumeEl.querySelector('.resume-name')?.innerText?.trim() || 'Candidate';
      const docHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>${name} Resume</title>
  <style>
    body { font-family: Calibri, Arial, sans-serif; color: #111827; margin: 28px; line-height: 1.45; }
    .resume-doc { max-width: 860px; margin: 0 auto; }
    .resume-header-section { border-bottom: 2px solid #0ea5e9; padding-bottom: 14px; margin-bottom: 16px; }
    .resume-name { font-size: 30px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
    .resume-target { font-size: 14px; color: #0369a1; margin-bottom: 8px; }
    .resume-contact { font-size: 12px; color: #334155; display: flex; flex-wrap: wrap; gap: 10px; }
    .resume-body { padding-top: 6px; }
    .rs-title { font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #0c4a6e; border-bottom: 1px solid #bae6fd; padding-bottom: 4px; margin: 14px 0 10px; font-weight: 700; }
    .rs-summary, .proj-desc, .edu-institution { font-size: 13px; color: #1f2937; }
    .skills-grid, .exp-techs { display: flex; flex-wrap: wrap; gap: 6px; }
    .skill-tag, .tech-pill { border: 1px solid #bae6fd; background: #f0f9ff; color: #075985; border-radius: 4px; padding: 2px 7px; font-size: 11px; }
    .exp-title-row { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
    .exp-role, .proj-name, .edu-degree { font-size: 14px; font-weight: 700; color: #0f172a; }
    .exp-company { font-size: 13px; color: #0369a1; }
    .exp-dates, .edu-meta { font-size: 11px; color: #64748b; }
    .exp-bullets { margin: 6px 0 0 0; padding-left: 18px; }
    .exp-bullets li { margin-bottom: 4px; font-size: 13px; color: #1f2937; }
    .proj-links { margin-top: 6px; display: flex; gap: 10px; }
    .proj-link { color: #0c4a6e; text-decoration: none; font-size: 11px; }
  </style>
</head>
<body>
  <div class="resume-doc">${resumeEl.innerHTML}</div>
</body>
</html>`;

      const blob = new Blob([docHtml], { type: 'application/msword' });
      const link = document.createElement('a');
      const objectUrl = URL.createObjectURL(blob);
      link.href = objectUrl;
      link.download = `${sanitizeFilename(name)}-buildmyfolio-resume.doc`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
    }

    function getPortfolioForExport() {
      const portfolio = state.latestPortfolio || state.generatedData?.portfolio;
      if (!portfolio) {
        alert('Generate your portfolio first.');
        return null;
      }
      return portfolio;
    }

    function escapeHtml(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => (
        ch === '&' ? '&amp;' :
          ch === '<' ? '&lt;' :
            ch === '>' ? '&gt;' :
              ch === '"' ? '&quot;' : '&#39;'
      ));
    }

    function normalizeUrl(url) {
      const raw = String(url || '').trim();
      if (!raw || /^javascript:/i.test(raw)) return '';
      return /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;
    }

function buildPortfolioStylesCss() {
      return `:root{
  --bg:#06060d;
  --surface:#0f0d1b;
  --surface2:#17142a;
  --text:#ecebff;
  --muted:#b6afd7;
  --accent:#b794f6;
  --accent2:#93c5fd;
  --border:#2f2a4a;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
  background:radial-gradient(circle at 15% 15%, rgba(183,148,246,.16), transparent 40%), radial-gradient(circle at 85% 80%, rgba(147,197,253,.12), transparent 45%), var(--bg);
  color:var(--text);
  line-height:1.6;
}
a{color:inherit}
.site{max-width:1120px;margin:0 auto;padding:2rem 1.1rem 4rem}
.hero{
  border:1px solid var(--border);
  background:linear-gradient(140deg, rgba(183,148,246,.2), rgba(147,197,253,.08));
  border-radius:20px;
  padding:3rem 1.6rem;
  text-align:center;
}
.name{font-size:clamp(2rem,6vw,3.6rem);font-weight:800;letter-spacing:-.03em;margin:0}
.tagline{font-size:1.1rem;color:#bfdbfe;margin:.6rem 0 1rem}
.about{max-width:760px;margin:0 auto;color:var(--muted)}
.chips{margin-top:1rem;display:flex;justify-content:center;flex-wrap:wrap;gap:.5rem}
.chip{
  padding:.25rem .7rem;
  border-radius:999px;
  border:1px solid rgba(183,148,246,.4);
  background:rgba(183,148,246,.14);
  font-size:.78rem;
}
.stats{
  margin-top:1.6rem;
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:.8rem;
}
.card{
  background:var(--surface2);
  border:1px solid var(--border);
  border-radius:14px;
  padding:1rem;
}
.stat-num{font-size:1.8rem;font-weight:800;background:linear-gradient(130deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-label{font-size:.75rem;color:var(--muted)}
.section-title{margin:2.2rem 0 .8rem;font-size:1rem;letter-spacing:.08em;text-transform:uppercase;color:#d8ccff}
.projects{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:1rem;
}
.project{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:14px;
  padding:1.1rem;
  position:relative;
  overflow:hidden;
}
.project::before{
  content:"";
  position:absolute;
  left:0;right:0;top:0;height:3px;
  background:var(--card-color, var(--accent));
}
.project-name{margin:.2rem 0 .4rem;font-size:1rem;font-weight:700}
.project-cat{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.project-desc{font-size:.9rem;color:#d8d7f1}
.tags{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.7rem}
.tag{
  border:1px solid rgba(147,197,253,.34);
  background:rgba(147,197,253,.1);
  color:#cbe4ff;
  border-radius:6px;
  font-size:.72rem;
  padding:.12rem .45rem;
}
.links{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:.7rem}
.link{
  text-decoration:none;
  font-size:.75rem;
  color:#bedbff;
}
.skills-wrap{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:14px;
  padding:1rem;
}
.skill-item{margin-bottom:.9rem}
.skill-head{display:flex;justify-content:space-between;font-size:.85rem;margin-bottom:.3rem}
.skill-track{height:8px;border-radius:999px;background:#2b2744;overflow:hidden}
.skill-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2))}
.contact{
  margin-top:2.2rem;
  border-top:1px solid var(--border);
  padding-top:1.2rem;
  color:var(--muted);
  display:flex;
  justify-content:space-between;
  gap:1rem;
  flex-wrap:wrap;
}
.contact-links{display:flex;gap:.9rem;flex-wrap:wrap}
.contact-links a{text-decoration:none;color:#c7ddff}
[data-reveal]{opacity:0;transform:translateY(14px);transition:all .55s ease}
[data-reveal].show{opacity:1;transform:none}
@media (max-width:900px){
  .stats{grid-template-columns:repeat(2,minmax(0,1fr))}
  .projects{grid-template-columns:1fr}
}
@media (max-width:560px){
  .site{padding:1.2rem .8rem 2rem}
  .hero{padding:2rem 1rem}
  .stats{grid-template-columns:1fr}
}`;
    }

    function buildPortfolioScriptJs() {
      return `document.querySelectorAll('[data-reveal]').forEach((el, idx) => {
  setTimeout(() => el.classList.add('show'), 60 * (idx + 1));
});
const yearEl = document.getElementById('portfolioYear');
if (yearEl) yearEl.textContent = new Date().getFullYear();`;
    }

    function buildPortfolioSiteContent(portfolio) {
      const bio = portfolio.bio || {};
      const stats = portfolio.stats || {};
      const contact = portfolio.contact || {};
      const projects = (portfolio.featured_projects || []).slice(0, 9);
      const skills = (portfolio.skills_visualization || []).slice(0, 8);
      const interests = (bio.interests || []).slice(0, 8);

      const displayName = escapeHtml(bio.headline || contact.name || 'Developer Portfolio');
      const tagline = escapeHtml(bio.tagline || 'AI-focused builder and engineer');
      const about = escapeHtml(bio.about || 'A portfolio generated with BuildMyFolio.');

      const statsHtml = [
        { label: 'Projects Built', value: Number(stats.projects_built) || projects.length || 0 },
        { label: 'Technologies', value: Number(stats.technologies) || 0 },
        { label: 'Years Coding', value: `${Number(stats.years_coding) || 1}+` },
        { label: 'Certifications', value: Number(stats.certifications) || 0 },
      ].map(item => `
    <article class="card" data-reveal>
      <div class="stat-num">${escapeHtml(item.value)}</div>
      <div class="stat-label">${escapeHtml(item.label)}</div>
    </article>
  `).join('');

      const interestsHtml = interests.map(i => `<span class="chip">${escapeHtml(i)}</span>`).join('');

      const projectsHtml = projects.map((proj, idx) => {
        const tags = (proj.tags || proj.technologies || []).slice(0, 6);
        const liveUrl = normalizeUrl(proj.live_url);
        const githubUrl = normalizeUrl(proj.github_url);
        const links = [
          liveUrl ? `<a class="link" href="${escapeHtml(liveUrl)}" target="_blank" rel="noopener noreferrer">Live Demo ↗</a>` : '',
          githubUrl ? `<a class="link" href="${escapeHtml(githubUrl)}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>` : '',
        ].filter(Boolean).join('');
        const cardColor = escapeHtml(proj.card_color || ['#b794f6', '#93c5fd', '#c4b5fd', '#a5b4fc'][idx % 4]);
        return `
      <article class="project" style="--card-color:${cardColor}" data-reveal>
        <div class="project-cat">${escapeHtml(proj.category || 'Engineering')}</div>
        <h3 class="project-name">${escapeHtml(proj.name || 'Project')}</h3>
        <p class="project-desc">${escapeHtml(proj.description || 'Project details not available.')}</p>
        <div class="tags">${tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}</div>
        ${links ? `<div class="links">${links}</div>` : ''}
      </article>
    `;
      }).join('');

      const skillsHtml = skills.map(skill => {
        const pct = Math.max(0, Math.min(100, Number(skill.proficiency) || 0));
        const skillNames = (skill.skills || []).slice(0, 3).map(escapeHtml).join(', ');
        return `
      <div class="skill-item" data-reveal>
        <div class="skill-head">
          <span>${escapeHtml(skill.category || 'Skill')} ${skillNames ? `<span style="color:#6fa6be;font-size:.75rem;">(${skillNames})</span>` : ''}</span>
          <strong>${pct}%</strong>
        </div>
        <div class="skill-track"><div class="skill-fill" style="width:${pct}%"></div></div>
      </div>
    `;
      }).join('');

      const contactLinks = [
        contact.email ? `<a href="mailto:${escapeHtml(contact.email)}">${escapeHtml(contact.email)}</a>` : '',
        normalizeUrl(contact.github) ? `<a href="${escapeHtml(normalizeUrl(contact.github))}" target="_blank" rel="noopener noreferrer">GitHub</a>` : '',
        normalizeUrl(contact.linkedin) ? `<a href="${escapeHtml(normalizeUrl(contact.linkedin))}" target="_blank" rel="noopener noreferrer">LinkedIn</a>` : '',
      ].filter(Boolean).join('');

      return `
<main class="site">
  <section class="hero" data-reveal>
    <h1 class="name">${displayName}</h1>
    <p class="tagline">${tagline}</p>
    <p class="about">${about}</p>
    ${interestsHtml ? `<div class="chips">${interestsHtml}</div>` : ''}
    <section class="stats">${statsHtml}</section>
  </section>

  ${projectsHtml ? `<h2 class="section-title">Featured Projects</h2><section class="projects">${projectsHtml}</section>` : ''}
  ${skillsHtml ? `<h2 class="section-title">Skills Overview</h2><section class="skills-wrap">${skillsHtml}</section>` : ''}

  <footer class="contact" data-reveal>
    <div>Built with BuildMyFolio</div>
    <div class="contact-links">${contactLinks}</div>
    <div>&copy; <span id="portfolioYear"></span> ${displayName}</div>
  </footer>
</main>`;
    }

    function buildPortfolioIndexHtml(portfolio) {
      return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml((portfolio.bio || {}).headline || 'Portfolio')}</title>
  <meta name="description" content="Portfolio site generated by BuildMyFolio" />
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
${buildPortfolioSiteContent(portfolio)}
<script src="./script.js"><\/script>
</body>

</html>`;
}

function buildPortfolioReadme(portfolio) {
const name = escapeHtml((portfolio.bio || {}).headline || 'Portfolio');
return `# ${name} Portfolio

This portfolio was generated by BuildMyFolio and is ready to deploy on GitHub Pages.

## Files
- \`index.html\`
- \`styles.css\`
- \`script.js\`

## Deploy On GitHub
1. Create a new GitHub repository.
2. Upload all files from this folder to the repository root.
3. Open repository settings.
4. Go to **Pages**.
5. Set source to **Deploy from a branch**.
6. Choose branch **main** and folder **/(root)**.
7. Save and wait for the deployment URL.

## Local Preview
Open \`index.html\` directly in a browser or serve with:

\`\`\`bash
python -m http.server 5500
\`\`\`
`;
}

function openPortfolioFullPage() {
const portfolio = getPortfolioForExport();
if (!portfolio) return;

const html = `
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml((portfolio.bio || {}).headline || 'Portfolio')}</title>
  <style>${buildPortfolioStylesCss()}</style>
</head>

<body>
  ${buildPortfolioSiteContent(portfolio)}
  <script>${buildPortfolioScriptJs()}<\/script>
</body>

</html>`;

const popup = window.open('', '_blank');
if (!popup) {
alert('Please allow popups to view the full-page portfolio.');
return;
}
popup.document.open();
popup.document.write(html);
popup.document.close();
}

async function downloadPortfolioZip() {
const portfolio = getPortfolioForExport();
if (!portfolio) return;
if (typeof JSZip === 'undefined') {
alert('ZIP library failed to load. Please check internet and try again.');
return;
}

const rootName = `${sanitizeFilename((portfolio.bio || {}).headline || 'portfolio-site')}-site`;
const zip = new JSZip();
const folder = zip.folder(rootName);
if (!folder) {
alert('Unable to create zip package.');
return;
}

folder.file('index.html', buildPortfolioIndexHtml(portfolio));
folder.file('styles.css', buildPortfolioStylesCss());
folder.file('script.js', buildPortfolioScriptJs());
folder.file('README.md', buildPortfolioReadme(portfolio));
folder.file('.nojekyll', '');
folder.file('.gitignore', '.DS_Store\n');

const blob = await zip.generateAsync({ type: 'blob' });
const link = document.createElement('a');
const objectUrl = URL.createObjectURL(blob);
link.href = objectUrl;
link.download = `${rootName}.zip`;
document.body.appendChild(link);
link.click();
document.body.removeChild(link);
setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
}

// ─── Load Sample Data ────────────────────────────────────────────────────────
function loadSampleData() {
  document.getElementById('name').value = 'Priya Sharma';
  document.getElementById('email').value = 'priya.sharma@email.com';
  document.getElementById('phone').value = '+91 9876543210';
  document.getElementById('location').value = 'Hyderabad, India';
  document.getElementById('linkedin').value = 'linkedin.com/in/priya-sharma';
  document.getElementById('github').value = 'github.com/priya-sharma';
  document.getElementById('targetRole').value = 'Full Stack Developer';
  document.getElementById('companyName').value = 'Google';
  document.getElementById('jobDescription').value = 'We are looking for a Full Stack Developer with expertise in React, Python, and cloud services. Experience with Docker, REST APIs, and PostgreSQL required. Knowledge of machine learning is a plus.';

  // Add sample skills
  const skills = ['Python', 'React', 'JavaScript', 'FastAPI', 'PostgreSQL', 'Docker', 'Machine Learning', 'Git'];
  skills.forEach(s => {
    state.skills.push(s);
    renderTag('skillsContainer', 'skills', s);
  });

  // Add education
  addEducation();
  const eduId = state.education[0].id;
  state.education[0] = { ...state.education[0], institution: 'IIT Hyderabad', degree: 'B.Tech', field: 'Computer Science', start_year: 2021, end_year: 2025, gpa: 8.7 };
  const eduEl = document.getElementById('edu-' + eduId);
  if (eduEl) {
    eduEl.querySelectorAll('input')[0].value = 'IIT Hyderabad';
    eduEl.querySelectorAll('input')[1].value = 'B.Tech';
    eduEl.querySelectorAll('input')[2].value = 'Computer Science';
    eduEl.querySelectorAll('input')[3].value = '8.7';
    eduEl.querySelectorAll('input')[4].value = '2021';
    eduEl.querySelectorAll('input')[5].value = '2025';
  }

  // Add experience
  addExperience();
  const expId = state.experience[0].id;
  state.experience[0] = { ...state.experience[0], company: 'TechStartup', role: 'Software Intern', start_date: 'May 2024', end_date: 'Aug 2024', description: 'Built REST APIs using FastAPI and deployed to AWS. Improved API response time by 40% through Redis caching. Collaborated with 5-member team using Agile methodology.', technologies: ['Python', 'FastAPI', 'AWS', 'Redis', 'PostgreSQL'] };

  // Add project
  addProject();
  const projId = state.projects[0].id;
  state.projects[0] = { ...state.projects[0], name: 'BuildMyFolio Assistant', description: 'AI-powered career document builder using NLP and machine learning. Analyzes job descriptions and generates tailored resumes with ATS optimization.', technologies: ['Python', 'React', 'FastAPI', 'TensorFlow', 'PostgreSQL'], github_url: 'github.com/priya-sharma/buildmyfolio', impact: 'Used by 200+ students, improved interview callback rate by 35%' };
}

// Auto-load sample data for demo
setTimeout(loadSampleData, 100);
