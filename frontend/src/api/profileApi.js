const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const API_URL = API_BASE_URL.endsWith("/analyze") ? API_BASE_URL : `${API_BASE_URL}/analyze`;

export async function analyzeProfile(answers) {
    const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            answers: answers.slice(0, 5),
            free_text: answers[5],
        }),
    });

    if (!response.ok) {
        throw new Error("Profile analysis failed");
    }

    return response.json();
}
