import React from 'react';

const Header = () => {
    return (
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem' }}>
            <img 
                src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
                alt="GitHub Logo" 
                width="60" 
                style={{ marginRight: '20px' }}
            />
            <div>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '5px' }}>GitHub Issue Analyzer</h1>
                <p style={{ color: '#8b949e', margin: 0, fontSize: '1.1rem' }}>
                    Transform messy issues into structured engineering insights instantly.
                </p>
            </div>
        </div>
    );
};

export default Header;
