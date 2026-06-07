export type LibraryEntry = {
  slug: string;
  title: string;
  duration: number;
  dominant: string;
  videoUrl: string;
};

export const LIBRARY: LibraryEntry[] = [
  { slug: "complaint_tiktok",  title: "Complaint TikTok",    duration: 15, dominant: "audio",    videoUrl: "/library/complaint_tiktok.mp4" },
  { slug: "finance_test_clip", title: "Finance Explainer",   duration: 11, dominant: "language", videoUrl: "/library/finance_test_clip.mp4" },
  { slug: "outfit_transition", title: "Outfit Transition",   duration: 15, dominant: "visual",   videoUrl: "/library/outfit_transition.mp4" },
  { slug: "walk_in_park",      title: "Walk in the Park",    duration: 15, dominant: "visual",   videoUrl: "/library/walk_in_park.mp4" },
  { slug: "flow_state_zetamac",title: "Flow State (Zetamac)",duration: 14, dominant: "audio",    videoUrl: "/library/flow_state_zetamac.mov" },
];
