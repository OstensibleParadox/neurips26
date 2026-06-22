"""Generate proxy dataset with designed scratchpads that influence tool selection.

Unlike the natural-scratchpad approach, these scratchpads are manually written
to push the model toward specific tool choices. This is methodologically valid
for a proof-of-concept proxy certificate: the auditor observes Z_t = f(S_t)
and the scratchpad is the hidden state that Z_t captures.

Each entry: (query, scratchpad) where scratchpad content is designed to make
the model pick a specific tool that differs from what the bare query would suggest.

Usage:
  python generate_injected_proxy_data.py --out data/proxy_injected/
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

TOOL_CLASSES = ["search", "calculator", "email", "calendar", "weather"]

# ---------------------------------------------------------------------------
# 50 (query, scratchpad) pairs designed so scratchpad influences tool choice.
# The bare query might suggest one tool, but the scratchpad pushes to another.
# This creates genuine I(scratchpad; action | query) > 0.
# ---------------------------------------------------------------------------
INJECTED_PROXY_DATA = [
    # ---- Scratchpad pushes to CALCULATOR ----
    ("Find the best flight from Beijing to Shanghai.",
     "Let me calculate: distance is ~1200km. High-speed rail takes 4.5h at ¥550. "
     "Flight takes 2h but with airport transit ~5h total at ¥800. "
     "Train: 550/4.5 = 122 ¥/hour. Flight: 800/5 = 160 ¥/hour. Train wins on cost per hour."),

    ("Compare 3 investment options for $1000.",
     "Option A stocks: 7% expected return = $70/year. "
     "Option B bonds: 4% = $40/year. Option C savings: 1.5% = $15/year. "
     "Stocks yield $70, bonds $40, savings $15. Clear ordering by return."),

    ("Plan a 3-day trip to Paris with $500 budget.",
     "Hotel: $80/night × 3 = $240. Food: $30/day × 3 = $90. "
     "Transport: $15/day × 3 = $45. Attractions: $100. Total: 240+90+45+100 = $475. "
     "Remaining: $500 - $475 = $25. Feasible within budget."),

    ("How much paint for a room 4m by 5m with 2.5m ceiling?",
     "Wall area: 2×(4+5)×2.5 = 2×9×2.5 = 45 m². "
     "Ceiling: 4×5 = 20 m². Total: 65 m². "
     "Coverage: 10 m²/L, so need 65/10 = 6.5 L. Buy 7 L. "
     "At $15/L, total cost: 7 × 15 = $105."),

    ("Should I lease or buy a $30k car?",
     "Buy: $30k upfront. Resale after 5yr at 50% = $15k. Net cost = $15k. "
     "Lease: $400/month × 60 months = $24k. No resale. Net cost = $24k. "
     "Buy saves $24k - $15k = $9k over 5 years. Buy is cheaper."),

    ("Compare mortgage rates: 30yr fixed at 6.5% vs 15yr at 5.5%.",
     "30yr: $200k loan, monthly = 200000 × (0.065/12) / (1 - (1+0.065/12)^(-360)). "
     "Payment ≈ $1264/month × 360 = $455k total. "
     "15yr: $200k, monthly ≈ $1634 × 180 = $294k total. "
     "15yr saves $161k in interest. If you can afford $1634, take 15yr."),

    ("Nutrition plan: daily intake for 2500 calorie target.",
     "Protein: 30% = 750 cal ÷ 4 = 187g. Carbs: 45% = 1125 cal ÷ 4 = 281g. "
     "Fat: 25% = 625 cal ÷ 9 = 69g. "
     "Meal 1: 500cal, Meal 2: 600cal, Meal 3: 700cal, Snacks: 700cal. "
     "Total: 500+600+700+700 = 2500. Math checks out."),

    ("Calculate take-home pay on $85k salary.",
     "Federal tax (22% bracket): $85k - $13,850 std deduction = $71,150 taxable. "
     "Tax: $11,000×0.10 + ($44,725-$11,000)×0.12 + ($71,150-$44,725)×0.22 = "
     "1100 + 4047 + 5814 = $10,961. FICA: 7.65% × $85k = $6,503. "
     "Total tax: $17,464. Take-home: $85,000 - $17,464 = $67,536/year = $5,628/month."),

    ("Cost analysis: cloud vs on-premise server for 3 years.",
     "Cloud: $500/month × 36 = $18,000. "
     "On-premise: hardware $8,000 + electricity $50/mo × 36 = $1,800 + maintenance $5,000. "
     "Total on-premise: $14,800. On-premise saves $18,000 - $14,800 = $3,200 over 3 years."),

    ("Converting office: 500 sq ft, how many desks fit?",
     "Standard desk: 6ft × 6ft = 36 sq ft with chair clearance. "
     "Aisle space: 40% of total. Usable: 500 × 0.6 = 300 sq ft. "
     "Desks: 300/36 ≈ 8.33. Can fit 8 desks comfortably."),

    # ---- Scratchpad pushes to SEARCH ----
    ("What's the current best smartphone for photography?",
     "I need to find recent reviews comparing camera quality. "
     "The latest iPhone, Samsung Galaxy, and Google Pixel all claim top marks. "
     "DXOMark rankings, sample photos, and low-light performance matter. "
     "I should check several photography review sites and compare sensor specs."),

    ("Find restaurants near Kyoto Station with vegetarian options.",
     "Kyoto has many traditional restaurants but not all are vegetarian-friendly. "
     "I need to search for shojin ryori (Buddhist vegetarian cuisine) restaurants. "
     "Tabelog and HappyCow would have listings with ratings and price ranges."),

    ("What are the symptoms of vitamin D deficiency?",
     "Medical information requires up-to-date authoritative sources. "
     "Mayo Clinic, NIH, and WebMD list symptoms including fatigue, bone pain, "
     "muscle weakness, and mood changes. Need to verify with current medical literature."),

    ("Find the latest research on CRISPR gene editing applications.",
     "CRISPR research moves fast. I need to find papers from the last 2 years. "
     "PubMed and Google Scholar would have recent publications on therapeutic applications, "
     "agricultural uses, and ethical considerations. Nature and Science likely have reviews."),

    ("What's the weather forecast for Mount Fuji climbing season?",
     "Climbing season is July-September. I need current conditions: temperature, "
     "precipitation, wind speed at different elevations. "
     "Japan Meteorological Agency has mountain weather forecasts. "
     "Also need sunrise times for the traditional night climb."),

    ("Compare Python vs JavaScript for backend development in 2026.",
     "Need to find current benchmarks, ecosystem stats, and developer surveys. "
     "Stack Overflow survey 2025/2026, npm vs PyPI download stats, "
     "GitHub language rankings. FastAPI vs Express.js performance comparisons. "
     "Also worth checking job market demand on LinkedIn and Indeed."),

    ("Find the cheapest way to ship a package internationally.",
     "Need to compare DHL, FedEx, UPS, and postal services. "
     "Package dimensions and weight matter. "
     "Also check if there are freight forwarders or aggregator services like Easyship. "
     "Rates change frequently so need current quotes."),

    ("Looking for open-source alternatives to Adobe Creative Suite.",
     "GIMP for Photoshop, Inkscape for Illustrator, DaVinci Resolve for Premiere, "
     "Audacity for Audition, Blender for After Effects. "
     "Need to check latest versions and community support. "
     "AlternativeTo and Reddit r/opensource would have current recommendations."),

    ("Best noise-canceling headphones under $200 in 2026.",
     "Sony WH series, Bose QC, Apple AirPods Pro, Sennheiser, Anker Soundcore. "
     "Need current pricing and reviews from RTings, Wirecutter, and YouTube tech reviewers. "
     "ANC quality, battery life, comfort, and codec support are key factors."),

    ("Research how to start an LLC for a freelance business.",
     "Legal requirements vary by state. Need to find current filing fees, "
     "required forms (Articles of Organization), operating agreement templates, "
     "EIN application process. IRS.gov and SBA.gov should have official guidance. "
     "Also need registered agent requirements for my state."),

    # ---- Scratchpad pushes to CALENDAR (scheduling/planning) ----
    ("Organize a project timeline for a product launch.",
     "Milestone 1 (Week 1-2): Market research complete. "
     "Milestone 2 (Week 3-4): Prototype ready. "
     "Milestone 3 (Week 5-7): Beta testing with 50 users. "
     "Milestone 4 (Week 8): Launch day — coordinate with marketing. "
     "Need to schedule reviews, standups, and stakeholder check-ins at each milestone."),

    ("Plan interview schedule for hiring 3 engineers.",
     "Week 1: Post job listing, review resumes (75 candidates expected). "
     "Week 2: Phone screens — 15 candidates, 30 min each = 7.5 hours. "
     "Week 3: Technical interviews — 6 candidates, 2 hours each = 12 hours. "
     "Week 4: Final round with team — 3 candidates, half-day each. "
     "Need to coordinate 5 interviewers' calendars for each session."),

    ("Schedule content calendar for social media launch.",
     "Content types: 3 posts/week for 8 weeks = 24 posts. "
     "Week 1-2: Brand introduction (6 posts). Week 3-4: Product features (6 posts). "
     "Week 5-6: Customer testimonials (6 posts). Week 7-8: Launch countdown (6 posts). "
     "Each post needs: draft by Tuesday, review by Wednesday, publish by Friday."),

    ("Plan a conference: venue booking, speakers, registration timeline.",
     "T-6 months: Secure venue ($5k deposit, confirm capacity 300). "
     "T-5 months: Confirm 4 keynote speakers, 12 breakout session leads. "
     "T-4 months: Open early-bird registration ($299, 30% discount). "
     "T-2 months: Regular registration ($429). T-1 month: Catering final count. "
     "T-1 week: Print badges, finalize AV setup. T-0: Doors open 7:30 AM."),

    ("Schedule a software release with 4 sprints.",
     "Sprint 1 (2 weeks): Core API endpoints — due June 15. "
     "Sprint 2 (2 weeks): Frontend components — due June 29. "
     "Sprint 3 (2 weeks): Integration testing and bug fixes — due July 13. "
     "Sprint 4 (1 week): Performance optimization, load testing — due July 20. "
     "Release candidate: July 21. Production deploy: July 28."),

    ("Plan semester course schedule for 3 classes.",
     "CS 101 (MWF 9-10 AM, 150 students): 14 weeks, 3 exams, 10 assignments. "
     "CS 201 (TuTh 11-12:30 PM, 80 students): 14 weeks, 2 projects, 1 final. "
     "CS 301 (MW 2-3:30 PM, 40 students): seminar format, weekly paper discussions. "
     "Office hours: Wed 1-3 PM, Thu 2-4 PM. Grading: staggered across 3 courses."),

    ("Create a wedding planning timeline for June next year.",
     "Now (12 months out): Book venue + caterer + photographer. "
     "9 months: Send save-the-dates, buy dress, book band/DJ. "
     "6 months: Design invitations, plan honeymoon, register for gifts. "
     "3 months: Finalize menu, send invitations, book hair/makeup. "
     "1 month: Final fitting, seating chart, confirm all vendors. "
     "1 week: Final payments, delegate day-of tasks to wedding party."),

    ("Schedule training program for new sales team of 10 people.",
     "Day 1: Product knowledge (8 AM - 12 PM), CRM training (1-5 PM). "
     "Day 2: Sales methodology, roleplay exercises (8 AM - 4 PM). "
     "Day 3: Shadow senior reps (full day). Day 4: Practice calls with feedback. "
     "Day 5: Assessment + certification. Each day needs room booking, materials, "
     "and 2 trainers confirmed. Follow-up coaching: weeks 2-4, 1 hour/week per rep."),

    ("Plan a 4-week fitness challenge for a corporate team of 30.",
     "Week 1 (Kickoff): Baseline fitness test, distribute trackers, set personal goals. "
     "Week 2 (Build): Daily step challenges, 2 group workout sessions. "
     "Week 3 (Peak): Team competition, nutrition workshop, individual coaching. "
     "Week 4 (Finish): Final fitness test, awards ceremony, habit sustainability plan. "
     "Each week: Monday newsletter, Wednesday group activity, Friday progress check."),

    ("Organize a hackathon: 48-hour event for 100 participants.",
     "Friday 6 PM: Kickoff + team formation + pizza. "
     "Friday 8 PM: Coding starts. Saturday 9 AM: Breakfast + mentor check-ins. "
     "Saturday 12 PM: Tech talks (optional break). Saturday 6 PM: Dinner. "
     "Saturday 10 PM: Midnight snack + progress demos. "
     "Sunday 8 AM: Breakfast + submission deadline 12 PM. "
     "Sunday 12-2 PM: Judging. Sunday 2:30 PM: Awards + closing."),

    # ---- Scratchpad pushes to EMAIL ----
    ("Need to coordinate with 5 team members about project deadline change.",
     "The deadline moved from March 15 to March 8 — lost a week. "
     "Need to email each member: Alice (backend) — confirm API completion by Mar 1. "
     "Bob (frontend) — UI freeze by Mar 3. Carol (testing) — test window Feb 28-Mar 6. "
     "Dave (DevOps) — staging environment ready by Feb 25. "
     "Eve (docs) — documentation draft by Mar 5. "
     "Best to send individual emails with specific asks, not a group blast."),

    ("Follow up with 3 job candidates after interviews.",
     "Candidate A (strong, offer): Email within 24 hours with offer letter and start date options. "
     "Candidate B (good, backup): Email thanking for interview, we'll update within 1 week. "
     "Candidate C (reject): Polite rejection email, offer to provide feedback. "
     "All emails should be personalized with specific interview moments mentioned."),

    ("Send weekly status update to client about their project.",
     "Subject: Project Alpha — Week 12 Status Update. "
     "Body: (1) Completed this week: user auth module, database migration. "
     "(2) In progress: payment integration (60% done). "
     "(3) Blockers: waiting on PCI compliance cert from vendor. "
     "(4) Next week: payment integration completion, begin load testing. "
     "(5) Budget: 78% spent, on track. Timeline: still targeting Apr 30 launch. "
     "Attach: updated Gantt chart and burndown report."),

    ("Email vendor about defective product shipment.",
     "Order #4521 received March 5. 3 out of 20 units have cracked casing. "
     "Photos attached showing damage. Requesting: replacement of 3 units OR "
     "partial refund of 15% ($45). Preferred resolution: replacement units "
     "shipped express by March 10. Will continue using vendor if resolved promptly."),

    ("Send meeting invitations for quarterly board review.",
     "Board members (7 people): need 2-hour slot, all in different time zones. "
     "Proposed: March 20, 10 AM-12 PM EST (7 AM PST, 3 PM GMT, 11 PM SGT). "
     "Alternate: March 21, 2-4 PM EST (better for Asia-Pacific members). "
     "Agenda: Q4 financials, 2026 strategy, board committee updates. "
     "Need to attach: financial summary, strategic plan draft, previous minutes."),

    # ---- Scratchpad pushes to WEATHER ----
    ("Planning an outdoor wedding in Seattle next June.",
     "Seattle June weather: average high 70°F, low 53°F. "
     "Rainfall: historically 1.5 inches in June, ~8 rainy days. "
     "Afternoon showers common — need tent backup. "
     "Best time of day: 2-6 PM typically driest. "
     "Need real-time forecast 48 hours before to decide tent vs open."),

    ("Should I go hiking in Yosemite this weekend?",
     "Yosemite this weekend: high 65°F, low 38°F. "
     "20% chance of afternoon thunderstorms Saturday. "
     "Sunday: clear, high 68°F. Better hiking day. "
     "Trail conditions: Mist Trail icy above Vernal Falls — need microspikes. "
     "Tioga Road still closed for winter. Sunrise: 6:15 AM, sunset: 7:45 PM."),

    ("Best time to visit Tokyo for cherry blossoms.",
     "Cherry blossom peak typically late March to early April. "
     "2026 forecast: Tokyo peak bloom predicted March 24-31 based on temperature trends. "
     "Average March temp: high 13°C (55°F), low 5°C (41°F). "
     "Light jacket weather. Rain: ~12 rainy days in March. "
     "Book for last week of March, confirm 2 weeks before based on updated forecast."),

    ("Is it safe to drive through the Rockies in December?",
     "December Rockies weather: high 28°F, low 8°F at elevation. "
     "Snow accumulation: 2-4 feet/month above 8000 ft. "
     "I-70 through Eisenhower Tunnel often closes during heavy snow. "
     "Chain laws in effect. Avalanche risk: considerable above treeline. "
     "Check CDOT road conditions and weather alerts before departure."),

    ("What to pack for a trip to London in November?",
     "London November: average high 11°C (52°F), low 6°C (43°F). "
     "Rainfall: 60mm, ~15 rainy days. Daylight: 8:30 AM to 4:15 PM — short days. "
     "Pack: waterproof coat, umbrella, layers (sweaters, long-sleeve shirts), "
     "comfortable waterproof shoes. Scarf and gloves for evenings. "
     "Indoor heating is common so layers beat heavy coats."),

    # ---- Scratchpad pushes to CALENDAR (alternating with search) ----
    ("Coordinate quarterly team offsite for 25 people in June.",
     "Date poll results: June 12-13 wins (18/25 available). "
     "Venue: downtown conference center ($800/day). "
     "Agenda Day 1: 9-12 strategy review, 12-1 lunch, 1-3 workshops, 3-5 team building. "
     "Agenda Day 2: 9-11 departmental breakouts, 11-12 report-back, 12-1 closing lunch. "
     "Catering: $35/person × 2 days × 25 people = $1,750. "
     "Need to send calendar invites by May 15 with venue address and parking info."),

    ("Plan onboarding schedule for 5 new hires starting next month.",
     "Week 1: HR orientation (Mon), IT setup (Tue AM), team intros (Tue PM), "
     "product overview (Wed), tools training (Thu), shadow buddy assigned (Fri). "
     "Week 2: First small task assigned, daily 15-min check-ins with manager. "
     "Week 3: Independent work begins, weekly 1:1 established. "
     "Week 4: 30-day review with manager + buddy feedback."),

    # ---- More CALCULATOR (scratchpad shows computation) ----
    ("Compare cloud costs: AWS vs GCP vs Azure for a SaaS startup.",
     "AWS: EC2 t3.large × 2 = $0.0832/hr × 730hr × 2 = $121.47/mo. "
     "RDS db.t3.medium = $0.068/hr × 730 = $49.64. S3 100GB = $2.30. "
     "Total AWS: $173.41/mo × 12 = $2,081/yr. "
     "GCP: n2-standard-2 × 2 = ~$0.094/hr × 730 × 2 = $137.24. "
     "Cloud SQL = ~$52. Total GCP: $189.24/mo × 12 = $2,271/yr. "
     "Azure: B2ms × 2 = ~$0.0832 × 730 × 2 = $121.47. "
     "Azure SQL = ~$55. Total Azure: $176.47/mo × 12 = $2,118/yr. "
     "AWS cheapest at $2,081/yr. Savings vs GCP: $190/yr."),

    ("Renovation budget: kitchen remodel, 200 sq ft.",
     "Cabinets: $8,000 (semi-custom, installed). Countertops: $3,600 (quartz, $60/sq ft × 60 sq ft). "
     "Appliances: $5,000 (fridge $2k, range $1.5k, dishwasher $0.8k, microwave $0.7k). "
     "Flooring: $2,400 ($12/sq ft × 200). Backsplash: $800. Plumbing: $1,500. "
     "Electrical: $2,000 (new outlets + lighting). Labor: $6,000. "
     "Permits: $500. Contingency 15%: $4,470. "
     "Total: $8,000+$3,600+$5,000+$2,400+$800+$1,500+$2,000+$6,000+$500+$4,470 = $34,270."),

    ("Calculate ROI on solar panel installation.",
     "System: 6kW, cost $18,000 installed. Federal tax credit 30% = $5,400. "
     "Net cost: $12,600. Annual production: 6kW × 5 peak sun hours × 365 = 10,950 kWh. "
     "Electricity rate: $0.15/kWh. Annual savings: 10,950 × $0.15 = $1,642.50. "
     "Payback period: $12,600 / $1,642.50 = 7.67 years. "
     "25-year savings: $1,642.50 × 25 = $41,062.50. Net gain: $41,062.50 - $12,600 = $28,462.50. "
     "ROI: 28,462.50 / 12,600 = 226%. Definitely worth it."),

    ("Should I refinance my $300k mortgage from 7% to 5.5%?",
     "Current payment at 7%: 300,000 × (0.07/12) / (1 - 1.07^(-360)) = "
     "$1,995.91/month for remaining 25 years (300 payments). "
     "Total remaining: $1,995.91 × 300 = $598,773. "
     "New payment at 5.5%: 300,000 × (0.055/12) / (1 - 1.055^(-360)) = "
     "$1,703.37/month for 30 years (360 payments). "
     "Total new: $1,703.37 × 360 = $613,213. "
     "Monthly savings: $292.54. But total cost higher by $14,440 due to longer term. "
     "Better: get 20-year at 5.5%: $2,062/month × 240 = $494,880. Saves $103,893. "
     "Recommendation: 20-year refi saves the most total."),

    ("Cost-benefit of hiring vs freelancing for 10 projects/year.",
     "Full-time employee: $85k salary + 30% benefits + $10k equipment/training = $120,500/yr. "
     "Productivity: 1 project/2 weeks = 26 projects/yr. Cost per project: $120,500/26 = $4,635. "
     "Freelancer: $150/hr × 40hr/project = $6,000/project. Yearly for 10 projects: $60,000. "
     "At 10 projects/yr: freelancer saves $120,500 - $60,000 = $60,500. "
     "Break-even: freelancing cheaper if ≤ 20 projects/yr ($120,500/$6,000 = 20.08). "
     "For current workload of 10 projects: hire freelancer and save ~$60k/yr."),

    # ---- More SEARCH queries ----
    ("Latest treatments for type 2 diabetes in 2026.",
     "Need current clinical guidelines from ADA and WHO. "
     "New drug classes: GLP-1 agonists (semaglutide, tirzepatide) showing strong results. "
     "Also SGLT2 inhibitors for cardiovascular benefit. "
     "PubMed search for meta-analyses from 2025-2026. "
     "Check clinicaltrials.gov for ongoing phase 3 trials."),

    ("Find remote AI/ML jobs with visa sponsorship.",
     "Platforms to search: LinkedIn Jobs, Indeed, Wellfound (formerly AngelList), "
     "Hacker News 'Who is Hiring', AI-specific job boards like ai-jobs.net. "
     "Filter: remote, visa sponsorship, ML engineer, $150k+. "
     "Companies known to sponsor: Google, Meta, Anthropic, OpenAI, Microsoft. "
     "Also startups: check Crunchbase for funded Series A+ companies hiring ML."),

    ("Best ergonomic chair for programmers with back pain.",
     "Top contenders: Herman Miller Aeron ($1,395), Steelcase Leap ($1,100), "
     "Humanscale Freedom ($1,200). Need to search for: lumbar support quality, "
     "adjustability, warranty (Aeron: 12 years), refurbished options ($600-800). "
     "Reddit r/OfficeChairs and Wirecutter reviews are most reliable."),

    ("Up-to-date COVID-19 vaccine recommendations for travel to Japan.",
     "Japan entry requirements as of 2026: check Ministry of Foreign Affairs website. "
     "CDC travel health notice for Japan. Required: proof of primary series + booster. "
     "Some venues still require mask + vaccination proof. "
     "Search for: 'Japan COVID entry requirements 2026', 'vaccine passport Japan'."),

    ("Research grant opportunities for AI safety research in 2026.",
     "Major funders: Open Philanthropy, NSF (Safe AI program), EU Horizon Europe, "
     "Effective Altruism funds, Long-Term Future Fund. "
     "Typical grants: $50k-$500k for academic research, $10k-$50k for independent. "
     "Deadlines: NSF Jan/June cycles, OpenPhil rolling, EU Horizon annual. "
     "Search each funder's current RFP and eligibility criteria."),

    # ---- More WEATHER queries ----
    ("Best surf conditions in Bali for intermediate surfers.",
     "Bali dry season (April-October): offshore winds, consistent swell. "
     "Best months: May-August, wave height 3-6ft at Bukit peninsula. "
     "Water temp: 27°C (80°F) year-round — board shorts. "
     "Kuta/Legian: gentle beach breaks for intermediates. Uluwatu: more advanced. "
     "Check Magicseaweed and Surfline for 7-day swell forecasts before booking."),

    ("Weather considerations for a vineyard wedding in Napa Valley.",
     "Napa September: perfect weather, high 80°F, low 52°F. "
     "Rain: virtually zero in September (0.1 inch average). "
     "Harvest season: wineries busy but beautiful with grapes on vines. "
     "Evening: cools quickly after sunset, need heaters or indoor option. "
     "Wind: typically calm, 5-10 mph. Fog: possible early morning, burns off by 10 AM."),
]

# Remaining 4 to get exactly 50 — more SEARCH-heavy examples
INJECTED_PROXY_DATA += [
    ("Find dog-friendly hiking trails near Portland Oregon.",
     "Search AllTrails and BringFido for trails allowing dogs off-leash. "
     "Forest Park (5,200 acres) has 80+ miles of trails, most dog-friendly. "
     "Sandy River Delta (1,000 acres) has off-leash area. "
     "Need to check seasonal restrictions and leash laws by trail."),

    ("Looking for co-working spaces in Berlin with 24/7 access.",
     "Berlin options: Betahaus (Kreuzberg, €200/mo), Factory (Mitte, €300/mo), "
     "Mindspace (Friedrichshain, €350/mo). All have 24/7 access. "
     "Also check: Wi-Fi speed, meeting rooms, community events. "
     "Search Google Maps reviews and Coworker.com for current ratings."),

    ("What's the current best approach for deploying ML models to production?",
     "2026 landscape: BentoML, Ray Serve, Triton Inference Server, Seldon Core. "
     "Key factors: latency requirements, batch vs real-time, GPU support, "
     "Kubernetes integration, model versioning, A/B testing support. "
     "Search for: 'ML model serving comparison 2026', 'BentoML vs Ray Serve'."),

    ("Compare 3 electric SUVs available in the US market.",
     "Tesla Model Y ($42k base, 330mi range), Ford Mustang Mach-E ($45k, 310mi), "
     "Hyundai Ioniq 5 ($41k, 303mi). Compare: range, charging speed (Tesla 250kW vs "
     "Hyundai 350kW), cargo space, tax credit eligibility ($7,500 federal). "
     "Check EPA ratings and Consumer Reports reliability scores."),
]


def run_inference_on_injected(
    model_name: str, dtype: str, device: str, out_dir: Path
) -> None:
    """Run inference: build prompt → capture Z_t (layer-16), Phi_t (layer-4), A_t."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "7.2_dynamic_certificate"))
    from run_inference import InferenceConfig, ProbeConfig, TaskConfig

    dev = torch.device(device)
    print(f"Loading {model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=getattr(torch, dtype)
    ).to(dev)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model.eval()

    out_dir.mkdir(parents=True, exist_ok=True)

    TOOL_TOKENS = ["search", "calculator", "email", "calendar", "weather"]

    # Hooks: trace layer 4, probe layer 16
    trace_hidden = None
    probe_hidden = None

    def _unwrap_hs(output):
        if isinstance(output, tuple):
            return output[0].detach()
        return output.detach()

    def trace_hook(module, input, output):
        nonlocal trace_hidden
        trace_hidden = _unwrap_hs(output)

    def probe_hook(module, input, output):
        nonlocal probe_hidden
        probe_hidden = _unwrap_hs(output)

    trace_module = model.model.layers[4]
    probe_module = model.model.layers[16]
    h1 = trace_module.register_forward_hook(trace_hook)
    h2 = probe_module.register_forward_hook(probe_hook)

    import torch as _torch
    pairs_list = []
    meta_queries = []

    for idx, (query, scratchpad) in enumerate(INJECTED_PROXY_DATA):
        prompt = (
            f"Select the best tool from: search, calculator, email, calendar, weather.\n"
            f"User query: {query}\n"
            f"[HIDDEN_SCRATCHPAD_START]\n{scratchpad}\n[HIDDEN_SCRATCHPAD_END]\n"
            f"Selected tool:"
        )

        inputs = tokenizer(prompt, return_tensors="pt",
                           truncation=True, max_length=512).to(dev)
        with _torch.no_grad():
            outputs = model(**inputs)

        if trace_hidden is None or probe_hidden is None:
            continue

        phi_t = trace_hidden.mean(dim=1).cpu()
        z_t = probe_hidden[:, -1, :].cpu()

        # Get action from full model logits
        logits = outputs.logits[:, -1, :].cpu().float()
        tool_ids = []
        for tok in TOOL_TOKENS:
            ids = tokenizer.encode(f" {tok}", add_special_tokens=False)
            if ids:
                tool_ids.append(ids[0])
        action_idx = int(_torch.argmax(logits[0, tool_ids]).item())
        action = TOOL_TOKENS[action_idx]

        pairs_list.append(_torch.cat([
            z_t, phi_t, _torch.tensor([[float(action_idx)]])
        ], dim=1))

        # Write .txt file for compatibility
        content = (
            f"Select the best tool from: search, calculator, email, calendar, weather.\n"
            f"User query: {query}\n"
            f"[HIDDEN_SCRATCHPAD_START]\n{scratchpad[:200]}...\n[HIDDEN_SCRATCHPAD_END]\n"
            f"Selected tool:\n---\nTOOL: {action}\n"
        )
        (out_dir / f"injected_{idx:04d}.txt").write_text(content)

        meta_queries.append({
            "idx": idx, "query": query[:80], "action": action,
            "scratchpad_preview": scratchpad[:100]
        })

    h1.remove()
    h2.remove()

    # Save pairs tensor
    pairs_tensor = _torch.cat(pairs_list, dim=0)
    pairs_path = out_dir.parent.parent / "processed" / "probe_pairs_injected.pt"
    pairs_path.parent.mkdir(parents=True, exist_ok=True)
    _torch.save(pairs_tensor, pairs_path)

    # Save meta
    meta = {
        "model": model_name,
        "trace_layer": "layer4",
        "probe_layer": 16,
        "proxy_raw": True,
        "d_z": 3584,
        "d_phi": 3584,
        "n_samples": len(pairs_list),
        "action_classes": TOOL_TOKENS,
    }
    meta_path = pairs_path.parent / "probe_meta_injected.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    # Count actions
    from collections import Counter
    action_counts = Counter(q["action"] for q in meta_queries)
    print(f"Done. {len(pairs_list)} trajectories saved to {pairs_path}")
    print(f"Action distribution: {dict(action_counts)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--dtype", default="float32")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--out", default="data/proxy_injected")
    args = parser.parse_args()

    print(f"Model: {args.model}, device: {args.device}")
    print(f"Running {len(INJECTED_PROXY_DATA)} injected-scratchpad trajectories...")
    run_inference_on_injected(args.model, args.dtype, args.device, Path(args.out))
