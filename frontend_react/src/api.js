const BACKEND_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

export const analyzeIssue = async (repoUrl, issueNumber) => {
  try {
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        repo_url: repoUrl,
        issue_number: parseInt(issueNumber, 10),
      }),
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
