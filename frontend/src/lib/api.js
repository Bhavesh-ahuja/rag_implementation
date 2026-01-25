const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const sendMessage = async (sessionId, query) => {
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: sessionId,
                query: query,
            }),
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("API Call Failed:", error);
        throw error;
    }
};

export const uploadDocument = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Upload Failed:", error);
        throw error;
    }
};

export const getFiles = async () => {
    try {
        const response = await fetch(`${API_URL}/files`);
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Fetch Files Failed:", error);
        return { files: [] };
    }
};

export const deleteFile = async (filename) => {
    try {
        const response = await fetch(`${API_URL}/files/${filename}`, {
            method: "DELETE",
        });
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Delete Failed:", error);
        throw error;
    }
};
