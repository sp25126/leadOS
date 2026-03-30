import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface BYOKKeys {
  apiKey: string;
  geminiKey: string;
  groqKey: string;
  googleMapsKey: string;
  hunterKey: string;
  [key: string]: string;
}

interface BYOKStore {
  keys: BYOKKeys;
  setKey: (k: keyof BYOKKeys, v: string) => void;
  clearAll: () => void;
}

const DEFAULT: BYOKKeys = {
  apiKey: "saumyavishwam@gmail",
  geminiKey: "",
  groqKey: "",
  googleMapsKey: "",
  hunterKey: "",
};

export const useBYOKStore = create<BYOKStore>()(
  persist(
    (set) => ({
      keys: DEFAULT,
      setKey: (k, v) => set((s) => ({ keys: { ...s.keys, [k]: v } })),
      clearAll: () => set({ keys: DEFAULT }),
    }),
    { name: "leados-byok-v2" }
  )
);
