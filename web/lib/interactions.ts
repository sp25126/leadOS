"use client";

export interface UserInteraction {
    id: string;
    type: "navigation" | "click" | "form_submit";
    path: string;
    label: string;
    timestamp: number;
    metadata?: Record<string, any>;
}

const STORAGE_KEY = "octagon_interaction_logs";
const MAX_LOGS = 100;

export const interactionLogger = {
    log: (interaction: Omit<UserInteraction, "id" | "timestamp">) => {
        if (typeof window === "undefined") return;

        const newLog: UserInteraction = {
            ...interaction,
            id: Math.random().toString(36).substring(2, 11),
            timestamp: Date.now(),
        };

        try {
            const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
            const updated = [newLog, ...existing].slice(0, MAX_LOGS);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
            
            // Dispatch custom event for real-time UI updates
            window.dispatchEvent(new CustomEvent("octagon_new_interaction", { detail: newLog }));
        } catch (e) {
            console.error("Failed to log interaction", e);
        }
    },

    getLogs: (): UserInteraction[] => {
        if (typeof window === "undefined") return [];
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
        } catch {
            return [];
        }
    },

    clearLogs: () => {
        if (typeof window === "undefined") return;
        localStorage.removeItem(STORAGE_KEY);
    }
};
