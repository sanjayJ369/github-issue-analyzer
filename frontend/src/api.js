const BACKEND_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

/**
 * Fetch available LLM providers from backend.
 * Returns array of {id, label, provider, model, is_available}
 */
export const getProviders = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/llm/providers`);
    
    if (!response.ok) {
      throw new Error("Failed to fetch providers");
    }
    
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch providers:", error);
    return [];
  }
};

/**
 * Analyze a GitHub issue.
 * @param {string} repoUrl - GitHub repository URL
 * @param {number} issueNumber - Issue number
 * @param {string|null} providerId - Optional LLM provider ID (auto-selects if only 1 available)
 */
export const analyzeIssue = async (repoUrl, issueNumber, providerId = null) => {
  try {
    const body = {
      repo_url: repoUrl,
      issue_number: parseInt(issueNumber, 10),
    };
    
    // Only include provider_id if explicitly set
    if (providerId) {
      body.provider_id = providerId;
    }
    
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const text = await response.text();
    let data;
    
    try {
        data = JSON.parse(text);
    } catch (e) {
        console.error("Failed to parse JSON response:", text);
        throw new Error(`Server Error: ${text.substring(0, 50)}... (Check Vercel Logs)`);
    }

    if (!response.ok) {
      throw new Error(data.detail || "Analysis failed");
    }

    return data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};
