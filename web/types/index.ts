export interface Lead {
    name: string;
    address: string;
    phone: string;
    email: string;
    website: string;
    has_website: boolean;
    rating: number;
    review_count: number;
    types: string;
    source: string;
    merged_sources: string;
    score: number;
    priority: "high" | "medium" | "low";
    reason: string;
    pain_points: string[];
    suggested_opening: string;
    tech_hints: string;
    social_media: string;
    website_live: boolean;
    has_contact_form: boolean;
    lat: number;
    lon: number;
}

export interface LeadSearchResponse {
    session_id: string;
    total: number;
    high_priority_count: number;
    medium_priority_count: number;
    low_priority_count: number;
    sources_used: string[];
    leads: Lead[];
}

export interface QuotaSource {
    remaining: number;
    used: number;
}

export interface QuotaStatus {
    overpass_main: QuotaSource;
    overpass_kumi: QuotaSource;
    overpass_private: QuotaSource;
    google_maps: QuotaSource;
    foursquare: QuotaSource;
    here_places: QuotaSource;
    hunter_io: QuotaSource;
    abstract_email: QuotaSource;
    [key: string]: QuotaSource;
}

export interface OutreachTask {
    task_id: string;
    status: "queued" | "running" | "done" | "error";
    session_id: string;
    wa_sent: number;
    email_sent: number;
    skipped: number;
    total_leads: number;
    started_at: number;
    completed_at: number | null;
    error: string | null;
}

export type ServiceType =
    | "website and AI automation"
    | "website design"
    | "booking system"
    | "social media automation"
    | "POS and inventory system"
    | "customer follow-up automation"
    | "online menu and ordering";

export const BUSINESS_TYPES = [
    "cafe", "restaurant", "clinic", "hospital", "shop",
    "salon", "gym", "hotel", "pharmacy", "school",
    "bakery", "bar", "supermarket", "dentist", "office",
] as const;

export const SERVICE_OPTIONS: { value: ServiceType; label: string }[] = [
    { value: "website and AI automation", label: "Website + AI Automation" },
    { value: "website design", label: "Website Design" },
    { value: "booking system", label: "Online Booking System" },
    { value: "social media automation", label: "Social Media Automation" },
    { value: "POS and inventory system", label: "POS & Inventory System" },
    { value: "customer follow-up automation", label: "Customer Follow-up (CRM)" },
    { value: "online menu and ordering", label: "Online Menu & Ordering" },
];
