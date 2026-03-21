import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface AppState {
    // Auth & Keys
    masterApiKey: string | null;
    geminiKey: string | null;
    brevoKey: string | null;
    setMasterApiKey: (key: string | null) => void;
    setGeminiKey: (key: string | null) => void;
    setBrevoKey: (key: string | null) => void;

    // App State
    sidebarOpen: boolean;
    toggleSidebar: () => void;
    activeSessionId: string | null;
    setActiveSessionId: (id: string | null) => void;

    // Referral / Bounty
    referralCode: string | null;
    setReferralCode: (code: string | null) => void;
}

export const useAppStore = create<AppState>()(
    persist(
        (set) => ({
            masterApiKey: null,
            geminiKey: null,
            brevoKey: null,
            setMasterApiKey: (key) => set({ masterApiKey: key }),
            setGeminiKey: (key) => set({ geminiKey: key }),
            setBrevoKey: (key) => set({ brevoKey: key }),

            sidebarOpen: true,
            toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
            activeSessionId: null,
            setActiveSessionId: (id) => set({ activeSessionId: id }),

            referralCode: null,
            setReferralCode: (code) => set({ referralCode: code }),
        }),
        {
            name: 'leados-hub-storage',
            storage: createJSONStorage(() => localStorage),
        }
    )
);
