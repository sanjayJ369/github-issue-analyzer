import React from 'react';

const Sidebar = () => {
    return (
        <aside style={{ width: '300px', marginLeft: '2rem', flexShrink: 0 }}>
            <div style={{ position: 'sticky', top: '2rem' }}>
                <img 
                    src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
                    alt="GitHub Logo" 
                    width="50" 
                    style={{ marginBottom: '1rem' }}
                />
                <h2 style={{ marginBottom: '1rem' }}>Control Panel</h2>
                <hr style={{ borderColor: 'var(--border-color)', margin: '1rem 0' }} />
                
                <div style={{ 
                    backgroundColor: 'rgba(56, 139, 253, 0.15)', 
                    border: '1px solid rgba(56, 139, 253, 0.4)', 
                    borderRadius: '6px',
                    padding: '1rem',
                    color: '#c9d1d9',
                    fontSize: '0.9rem'
                }}>
                    💡 <strong>Pro Tip</strong>: Use a `GITHUB_TOKEN` in the backend for higher limits.
                </div>
                
                <hr style={{ borderColor: 'var(--border-color)', margin: '1rem 0' }} />
                <p style={{ color: '#8b949e', fontSize: '0.8rem' }}>
                    Powered by Google Gemini 2.0 Flash
                </p>
            </div>
        </aside>
    );
};

export default Sidebar;
